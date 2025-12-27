import os
import sys
import json
import argparse
from google import genai
from google.genai import types
from colorama import Fore, Style, init

init(autoreset=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_with_gemini(code_context, doc_text):
    client = genai.Client(api_key=GEMINI_API_KEY)
    models = ['gemini-2.0-flash', 'gemini-2.0-flash-001', 'gemini-1.5-flash', 'gemini-flash-latest']
    
    prompt = f"""
    You are DockGuard. Compare the CODE CHANGES against the DOCUMENTATION.
    
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

    --- CODE CHANGES ---
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
            return json.loads(response.text)
        except Exception as e:
            print(f"<!-- Model {model_name} failed: {e} -->")
            continue
    
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DockDesk AI Auditor')
    parser.add_argument('--files', nargs='+', help='List of changed files', required=True)
    parser.add_argument('--doc', help='Path to documentation file', required=True)
    
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not found.")
        sys.exit(1)

    # 1. Read Documentation
    try:
        with open(args.doc, 'r', encoding='utf-8') as f:
            doc_text = f.read()
    except FileNotFoundError:
        print(f"Error: Documentation file '{args.doc}' not found.")
        sys.exit(1)

    # 2. Read Changed Files
    code_context = ""
    current_script = os.path.basename(__file__)
    
    for file_path in args.files:
        # Ignore the agent itself and the documentation file to avoid self-referential confusion
        if file_path.endswith(current_script) or file_path == args.doc:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_context += f"\n\n--- FILE: {file_path} ---\n{f.read()}"
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")

    if not code_context.strip():
        print("No code content found in changed files.")
        sys.exit(0)

    # 3. Analyze
    result = analyze_with_gemini(code_context, doc_text)

    def calculate_risk(text):
        text = text.lower()
        high_keywords = ['auth', 'security', 'password', 'key', 'token', 'billing', 'payment', 'admin', 'access']
        medium_keywords = ['api', 'endpoint', 'database', 'schema', 'config', 'deprecated']
        
        if any(k in text for k in high_keywords):
            return "High", "🔴"
        if any(k in text for k in medium_keywords):
            return "Medium", "🟠"
        return "Low", "🟢"

    def generate_slack_payload(issue, risk, suggestion):
        return {
            "text": "🚨 *DockDesk Alert: Documentation Drift Detected*",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Risk Level:* {risk}\n*Issue:* {issue}"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*AI Suggestion:* {suggestion}"}
                }
            ]
        }

    if result:
        if result.get("has_contradiction"):
            risk_level, risk_icon = calculate_risk(result.get('reason') + " " + code_context)
            
            print(f"### 🛡️ Semantic Audit Report")
            print(f"| Status | Risk Score | Issue |")
            print(f"| :--- | :--- | :--- |")
            print(f"| 🔴 **FAIL** | {risk_icon} **{risk_level}** | {result.get('reason')} |")
            
            print(f"\n**🤖 AI Suggestion:** {result.get('suggested_fix_description')}")
            
            if result.get('new_doc_content'):
                print(f"\n<details><summary><b>✨ View Self-Healed Documentation</b></summary>\n")
                print(f"```markdown\n{result.get('new_doc_content')}\n```")
                print(f"\n</details>")

            # Simulate Enterprise Integration
            slack_payload = generate_slack_payload(result.get('reason'), risk_level, result.get('suggested_fix_description'))
            print(f"\n<details><summary><b>🔌 Enterprise Integration (Mock Slack Payload)</b></summary>\n")
            print(f"```json\n{json.dumps(slack_payload, indent=2)}\n```")
            print(f"\n</details>")
            
            sys.exit(1) # Fail the workflow
        else:
            print(f"### 🛡️ Semantic Audit Report")
            print(f"| Status | Risk Score | Issue |")
            print(f"| :--- | :--- | :--- |")
            print(f"| 🟢 **PASS** | 🟢 Low | No contradictions found. |")
            sys.exit(0)
    else:
        print(f"❌ Analysis Failed. Could not connect to any Gemini models.")
        sys.exit(1)
