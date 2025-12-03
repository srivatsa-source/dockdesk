import os
import sys
import json
import requests
import google.generativeai as genai
from colorama import Fore, Style, init

init(autoreset=True)

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")

# We use the variable name 'OPENAI_API_KEY' because that is what action.yml sends,
# but we treat it as a Google Gemini Key.
api_key = os.getenv("OPENAI_API_KEY") 
if not api_key:
    print(f"{Fore.RED}Error: API Key not found.{Style.RESET_ALL}")
    sys.exit(1)

genai.configure(api_key=api_key)

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found -> {filepath}")
        sys.exit(1)

def post_pr_comment(reason, suggested_fix, model_name):
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY or not GITHUB_EVENT_PATH:
        print(f"{Fore.YELLOW}Skipping comment: Missing GitHub context.{Style.RESET_ALL}")
        return

    try:
        with open(GITHUB_EVENT_PATH, 'r') as f:
            event_data = json.load(f)
            # Handle both Pull Request and Issue Comment events
            pr_number = event_data.get('pull_request', {}).get('number') or \
                        event_data.get('issue', {}).get('number')
            if not pr_number: return
    except Exception:
        return

    comment_body = f"""
### 🚨 DockDesk: Documentation Drift Detected
**Reason:** {reason}

**Suggested Fix:**
```markdown
{suggested_fix}
```
(Automated by DockDesk running on {model_name})
"""

    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    requests.post(url, json={"body": comment_body}, headers=headers)
    print(f"{Fore.GREEN}✅ Comment posted to PR #{pr_number}{Style.RESET_ALL}")

def check_documentation_drift(code_content, doc_content):
    print(f"{Fore.CYAN}🔍 Analyzing with Gemini...{Style.RESET_ALL}")

    # 🚨 UPDATED: Use the models found in your logs
    models_to_try = [
        'gemini-2.0-flash',       # The new standard (fastest)
        'gemini-2.0-flash-lite',  # Lightweight version
        'gemini-flash-latest',    # Stable alias
        'gemini-pro-latest'       # Fallback
    ]

    prompt = f"""
You are 'DocuGuard'. Check if the CODE logic contradicts the DOCS.
CRITICAL RULES:
1. Flag CONTRADICTIONS only.
2. Output strictly valid JSON: {{"has_contradiction": true/false, "reason": "...", "suggested_fix": "..."}}

--- DOCS ---
{doc_content}
--- CODE ---
{code_content}
"""

    for model_name in models_to_try:
        print(f"Trying model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            # Return result immediately if successful
            return json.loads(response.text), model_name
        except Exception as e:
            print(f"{Fore.YELLOW}Failed with {model_name}: {e}{Style.RESET_ALL}")
            continue

    # If we get here, ALL models failed.
    print(f"{Fore.RED}❌ All models failed.{Style.RESET_ALL}")
    sys.exit(1)

# ---------------------------------------------------------
# 3. MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    code_path = sys.argv[1]
    doc_path = sys.argv[2]

    code_text = read_file(code_path)
    doc_text = read_file(doc_path)

    result, used_model = check_documentation_drift(code_text, doc_text)

    if result.get("has_contradiction"):
        print(f"\n{Fore.RED}🚨 DRIFT DETECTED!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Reason:{Style.RESET_ALL} {result.get('reason')}")
        
        post_pr_comment(result.get("reason"), result.get("suggested_fix"), used_model)
        
        sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}✅ Accurate.{Style.RESET_ALL}")