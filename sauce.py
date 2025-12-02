import os
import sys
import json
from openai import OpenAI
from colorama import Fore, Style, init

init(autoreset=True)

# 1. SETUP CLIENT
# We ask the computer: "Give me the value stored in the variable named OPENAI_API_KEY"
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    # This error prints if the computer (or GitHub) doesn't have the secret loaded
    print(f"{Fore.RED}Error: OPENAI_API_KEY not found in environment variables.{Style.RESET_ALL}")
    sys.exit(1)

client = OpenAI(api_key=api_key)
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found -> {filepath}")
        sys.exit(1)

def check_documentation_drift(code_content, doc_content):
    print(f"{Fore.CYAN}🔍 Analyzing file logic vs documentation...{Style.RESET_ALL}")
    
    system_prompt = """
    You are 'DocuGuard', a paranoid QA engineer. 
    Your ONLY job is to find discrepancies between Code and Docs.
    
    CRITICAL RULES:
    1. If the code has a check (e.g., 'if (!twoFactor)...') and the docs say it's not required, THAT IS A DRIFT.
    2. If the code adds a new parameter not in the docs, THAT IS A DRIFT.
    3. Do not be lenient. If you are unsure, flag it as a potential drift.
    4. You must respond in valid JSON format: {"has_contradiction": true/false, "reason": "...", "suggested_fix": "..."}
    """
    user_prompt = f"--- DOCS ---\n{doc_content}\n\n--- CODE ---\n{code_content}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    # 2. READ ARGUMENTS FROM TERMINAL
    if len(sys.argv) < 3:
        print(f"{Fore.YELLOW}Usage: py sauce.py <code_file> <doc_file>{Style.RESET_ALL}")
        sys.exit(1)

    code_path = sys.argv[1]
    doc_path = sys.argv[2]

    # 3. RUN THE CHECK
    code_text = read_file(code_path)
    doc_text = read_file(doc_path)
    
    result = check_documentation_drift(code_text, doc_text)

    # 4. REPORT
    if result.get("has_contradiction"):
        print(f"\n{Fore.RED}🚨 DRIFT DETECTED in {doc_path}!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Reason:{Style.RESET_ALL} {result.get('reason')}")
        print(f"\n{Fore.GREEN}📝 Suggested Fix:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{result.get('suggested_fix')}")
    else:
        print(f"\n{Fore.GREEN}✅ {doc_path} is accurate.{Style.RESET_ALL}")