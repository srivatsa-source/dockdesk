import os
import sys
import json
import requests
import google.generativeai as genai
from colorama import Fore, Style, init

init(autoreset=True)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print(f"{Fore.RED}Error: API Key not found.{Style.RESET_ALL}")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# GITHUB API HELPERS
# ---------------------------------------------------------
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
def analyze_with_gemini(diff_text, doc_text):
    print(f"{Fore.CYAN}🧠 Analyzing logic with Gemini 2.0...{Style.RESET_ALL}")
    
    models = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    
    prompt = f"""
    You are DockGuard. Compare the PR CODE CHANGES (Diffs) against the DOCUMENTATION.
    
    RULES:
    1. Focus on LOGIC CONTRADICTIONS (e.g., Code adds 'admin_only' check, Docs say 'public').
    2. IGNORE refactors or variable renames.
    3. If the code introduces a NEW feature not in docs, suggest adding it.
    4. Output strictly valid JSON: {{"has_contradiction": true/false, "reason": "...", "suggested_fix": "..."}}

    --- DOCUMENTATION (Source of Truth) ---
    {doc_text}

    --- CODE CHANGES (The Diff) ---
    {diff_text}
    """

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            return json.loads(response.text), model_name
        except:
            continue
    
    return None, None

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    # We still take doc_path as an argument because we need a "Source of Truth"
    if len(sys.argv) < 3:
        # If no code file provided, we assume "Smart Mode" (Only doc provided)
        # Usage: python sauce.py "SMART_MODE" "docs.md"
        pass

    # Read args (We might ignore code_path in smart mode)
    code_path_arg = sys.argv[1]
    doc_path = sys.argv[2]

    # 1. Read Documentation
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_text = f.read()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Documentation file '{doc_path}' not found.{Style.RESET_ALL}")
        sys.exit(1)

    # 2. Get Code Context (Smart vs Manual)
    pr_number = get_pr_details()
    
    if pr_number:
        # SMART MODE: Ignore local file arg, look at the PR
        code_context = get_pr_diffs(pr_number)
        if not code_context:
            print("No code changes found in this PR to analyze.")
            sys.exit(0)
    else:
        # MANUAL MODE: Use the file passed in args (for local testing)
        print(f"{Fore.YELLOW}No PR detected. Running in local/manual mode on {code_path_arg}{Style.RESET_ALL}")
        try:
            with open(code_path_arg, 'r', encoding='utf-8') as f:
                code_context = f.read()
        except:
            sys.exit(1)

    # 3. Analyze
    result, model = analyze_with_gemini(code_context, doc_text)

    if result and result.get("has_contradiction"):
        print(f"\n{Fore.RED}🚨 DRIFT DETECTED!{Style.RESET_ALL}")
        print(f"Reason: {result.get('reason')}")
        
        # Post comment if in a PR
        if pr_number:
            body = f"### 🚨 DockDesk detected a conflict\n**Reason:** {result['reason']}\n\n**Suggestion:**\n```markdown\n{result['suggested_fix']}\n```\n*(Analyzed {len(code_context)} chars of code changes)*"
            post_comment(pr_number, body)
            sys.exit(1) # Fail build
    else:
        print(f"\n{Fore.GREEN}✅ No contradictions found.{Style.RESET_ALL}")