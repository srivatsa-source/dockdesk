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
    You are 'DocuGuard', a code compliance auditor.
    Your job is to check if the code logic CONTRADICTS the documentation.
    
    CRITICAL INSTRUCTIONS:
    1. CONTRADICTION ONLY: Only flag if the documentation says X but the code does Y. 
    2. IGNORE OMISSIONS: If the code does something (like 'return true') and the docs are silent about it, assume it is CORRECT. Do not flag missing details.
    3. INFER INTENT: If the code says `if (age < 18) error`, and the docs say "18+ required", that is a MATCH. Do not demand explicit text saying "Over 18 is allowed".
    4. Output JSON: {"has_contradiction": true/false, "reason": "...", "suggested_fix": "..."}
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

  