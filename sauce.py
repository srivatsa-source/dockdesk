import os
import sys
import json
import requests
import argparse
from google import genai
from google.genai import types
from colorama import Fore, Style, init

init(autoreset=True)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------
# GITHUB API HELPERS
# ---------------------------------------------------------
def set_github_output(name, value):
    """Sets a GitHub Action output variable."""
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            # Handle multiline strings safely
            if "\n" in str(value):
                delimiter = f"EOF_{os.urandom(4).hex()}"
                f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{name}={value}\n")

def get_pr_details():
    """Extracts PR number from the GitHub Event JSON."""
    if not GITHUB_EVENT_PATH: return None
    try:
        with open(GITHUB_EVENT_PATH, 'r') as f:
            data = json.load(f)
            return data.get('pull_request', {}).get('number')
    except:
        return None

def get_pr_diffs(pr_number):
    """
    Fetches the actual code changes (diffs) from the Pull Request.
    This makes the bot 'Smart' - it sees what you changed automatically.
    """
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        print(f"{Fore.RED}Missing GitHub Token or Repo info.{Style.RESET_ALL}")
        return None

    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print(f"{Fore.CYAN}📥 Fetching changed files from PR #{pr_number}...{Style.RESET_ALL}")
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"{Fore.RED}Failed to fetch PR files: {resp.text}{Style.RESET_ALL}")
        return None

    files = resp.json()
    combined_diff = ""
    
    # Filter for code files only (ignore images, json, etc if needed)
    valid_extensions = ('.js', '.ts', '.py', '.java', '.go', '.rb', '.cpp', '.h', '.cs', '.php')
    
    count = 0
    for f in files:
        filename = f['filename']
        if filename.endswith(valid_extensions):
            patch = f.get('patch', '(No text diff available)')
            combined_diff += f"\n\n--- FILE: {filename} ---\n{patch}"
            count += 1
            
    print(f"{Fore.GREEN}✅ Found {count} code files changed.{Style.RESET_ALL}")
    return combined_diff

def post_comment(pr_number, body):
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    requests.post(url, json={"body": body}, headers=headers)
    print(f"{Fore.GREEN}✅ Comment posted.{Style.RESET_ALL}")

# ---------------------------------------------------------
# AI ANALYSIS
# ---------------------------------------------------------
def analyze_with_gemini(code_context, doc_text, context_type="diff", verbose=True):
    if verbose:
        print(f"{Fore.CYAN}🧠 Analyzing logic with Gemini 2.0...{Style.RESET_ALL}")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    # Updated model list based on available models for the key
    models = [
        'gemini-2.0-flash',
        'gemini-2.0-flash-001',
        'gemini-flash-latest',
        'gemini-2.0-flash-exp'
    ]
    
    prompt_context = "PR CODE CHANGES (Diffs)" if context_type == "diff" else "FULL SOURCE CODE"

    prompt = f"""
    You are DockGuard. Compare the {prompt_context} against the DOCUMENTATION.
    
    RULES:
    1. Focus on LOGIC CONTRADICTIONS (e.g., Code adds 'admin_only' check, Docs say 'public').
    2. IGNORE refactors or variable renames.
    3. If the code introduces a NEW feature not in docs, suggest adding it.
    4. Output strictly valid JSON.
    
    JSON FORMAT:
    {{
        "has_contradiction": true/false,
        "reason": "Concise explanation",
        "suggested_fix_description": "Human readable suggestion",
        "new_doc_content": "The FULL updated documentation text with the fix applied. Return null if no contradiction."
    }}

    --- DOCUMENTATION (Source of Truth) ---
    {doc_text}

    --- {prompt_context} ---
    {code_context}
    """

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text), model_name
        except Exception as e:
            if verbose:
                print(f"{Fore.YELLOW}Warning: Model {model_name} failed: {e}{Style.RESET_ALL}")
            continue
    
    return None, None

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DockDesk AI Auditor')
    parser.add_argument('code_path', help='Path to code file or "AUTO" to scan PR changes')
    parser.add_argument('doc_path', help='Path to documentation file')
    parser.add_argument('--json', action='store_true', help='Output result as JSON (useful for agents)')
    parser.add_argument('--fail-on-drift', type=str, default='true', help='Fail exit code on drift (true/false)')
    
    args = parser.parse_args()

    # Check API Key
    if not GEMINI_API_KEY:
        if args.json:
            print(json.dumps({"error": "GEMINI_API_KEY environment variable not found."}))
            sys.exit(1)
        else:
            print(f"{Fore.RED}Error: GEMINI_API_KEY environment variable not found.{Style.RESET_ALL}")
            sys.exit(1)

    # 1. Read Documentation
    try:
        with open(args.doc_path, 'r', encoding='utf-8') as f:
            doc_text = f.read()
    except FileNotFoundError:
        if args.json:
            print(json.dumps({"error": f"Documentation file '{args.doc_path}' not found."}))
            sys.exit(1)
        else:
            print(f"{Fore.RED}Error: Documentation file '{args.doc_path}' not found.{Style.RESET_ALL}")
            sys.exit(1)

    # 2. Get Code Context (Smart vs Manual)
    pr_number = get_pr_details()
    code_context = None
    context_type = "diff"
    
    if pr_number and args.code_path == "AUTO":
        # SMART MODE: Ignore local file arg, look at the PR
        code_context = get_pr_diffs(pr_number)
        if not code_context:
            if args.json:
                print(json.dumps({"message": "No code changes found in this PR."}))
            else:
                print("No code changes found in this PR to analyze.")
            sys.exit(0)
    else:
        # MANUAL MODE: Use the file passed in args (for local testing)
        if not args.json:
            print(f"{Fore.YELLOW}No PR detected. Running in local/manual mode on {args.code_path}{Style.RESET_ALL}")
        
        context_type = "full_source"
        try:
            with open(args.code_path, 'r', encoding='utf-8') as f:
                code_context = f.read()
        except FileNotFoundError:
             if args.json:
                print(json.dumps({"error": f"Code file '{args.code_path}' not found."}))
                sys.exit(1)
             else:
                print(f"{Fore.RED}Error: Code file '{args.code_path}' not found.{Style.RESET_ALL}")
                sys.exit(1)
        except Exception as e:
            sys.exit(1)

    # 3. Analyze
    result, model = analyze_with_gemini(code_context, doc_text, context_type=context_type, verbose=not args.json)

    if args.json:
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({"error": "AI Analysis failed. Check API Key quota or model availability."}))
            sys.exit(1)
    else:
        if result:
            if result.get("has_contradiction"):
                print(f"\n{Fore.RED}🚨 DRIFT DETECTED!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Reason:{Style.RESET_ALL} {result.get('reason')}")
                print(f"{Fore.YELLOW}Suggestion:{Style.RESET_ALL} {result.get('suggested_fix_description')}")
                
                # Interactive Fix Mode
                if result.get("new_doc_content"):
                    print(f"\n{Fore.CYAN}🤖 DockDesk can automatically fix the documentation.{Style.RESET_ALL}")
                    choice = input(f"Do you want to overwrite '{args.doc_path}' with the fixed version? [y/N]: ").strip().lower()
                    if choice == 'y':
                        try:
                            with open(args.doc_path, 'w', encoding='utf-8') as f:
                                f.write(result['new_doc_content'])
                            print(f"{Fore.GREEN}✅ Documentation updated successfully!{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}❌ Failed to write file: {e}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️ Changes skipped.{Style.RESET_ALL}")

                # Post comment if in a PR
                if pr_number:
                    body = f"### 🚨 DockDesk detected a conflict\n**Reason:** {result['reason']}\n\n**Suggestion:**\n{result.get('suggested_fix_description')}\n\n*(Analyzed {len(code_context)} chars of code changes)*"
                    post_comment(pr_number, body)
                
                # Set GitHub Outputs
                set_github_output("drift_detected", "true")
                set_github_output("suggested_fix", result.get('suggested_fix_description', ''))
                set_github_output("new_doc_content", result.get('new_doc_content', ''))

                # Exit logic based on fail-on-drift flag
                if args.fail_on_drift.lower() == 'true':
                    sys.exit(1) # Fail build
                else:
                    print(f"{Fore.YELLOW}⚠️ Drift detected, but fail-on-drift is false. Exiting with success.{Style.RESET_ALL}")
                    sys.exit(0)
            else:
                print(f"\n{Fore.GREEN}✅ No contradictions found. Docs are in sync.{Style.RESET_ALL}")
                set_github_output("drift_detected", "false")
        else:
            print(f"\n{Fore.RED}❌ Analysis Failed. Could not connect to any Gemini models.{Style.RESET_ALL}")
            sys.exit(1)