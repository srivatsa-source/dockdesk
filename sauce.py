import os
import sys
import json
import google.generativeai as genai
from colorama import Fore, Style, init

init(autoreset=True)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print(f"{Fore.RED}Error: API Key not found.{Style.RESET_ALL}")
    sys.exit(1)

genai.configure(api_key=OPENAI_API_KEY)

# Initialize Model
# Using a list of models to try for robustness
model_name = 'gemini-2.0-flash'
try:
    model = genai.GenerativeModel(model_name)
except:
    model = genai.GenerativeModel('gemini-pro')

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File '{path}' not found.{Style.RESET_ALL}")
        sys.exit(1)

def run_audit(code_path, doc_path):
    print(f"{Fore.CYAN}--- DockDesk AI Knowledge Guardrail ---")
    print(f"{Fore.YELLOW}Target:{Style.RESET_ALL} Preventing Knowledge Decay in {doc_path}")
    
    code_content = read_file(code_path)
    doc_content = read_file(doc_path)

    # --- UPGRADED PROMPT FOR CEO DEMO ---
    system_prompt = f"""
    You are DockDesk, a Knowledge Integrity Agent for Atomicwork.
    
    1. ANALYZE: Compare the Code Logic ({code_path}) vs. Documentation ({doc_path}).
    2. DETECT: Find contradictions that would cause an AI Support Agent to hallucinate/fail.
    3. FIX: If a contradiction exists, REWRITE the specific section of the documentation to match the code.

    DATA:
    --- DOCS ---
    {doc_content}
    --- CODE ---
    {code_content}

    OUTPUT FORMAT (Strict JSON):
    {{
        "status": "FAIL" or "PASS",
        "risk_level": "HIGH" or "LOW",
        "impact": "One sentence explaining why an AI Agent would give wrong answers based on the old docs.",
        "suggested_fix": "The exact Markdown text to replace the outdated section."
    }}
    """

    print(f"{Fore.CYAN}🤖 Simulating Atomicwork Knowledge Scan...{Style.RESET_ALL}")
    
    try:
        response = model.generate_content(system_prompt)
        # In a real app, parse the JSON. For the demo, we just print the raw text nicely.
        result = response.text.strip()
        
        # Clean up JSON formatting for terminal display
        import json
        
        # Strip markdown code blocks if Gemini adds them
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "")
        elif result.startswith("```"):
            result = result.replace("```", "")
            
        data = json.loads(result)

        print("\n" + "="*40)
        
        if data["status"] == "FAIL":
            print(f"{Fore.RED}❌ KNOWLEDGE DRIFT DETECTED")
            print(f"{Fore.YELLOW}📉 Hallucination Risk: {Fore.RED}{data['risk_level']}")
            print(f"{Fore.WHITE}⚠️ Business Impact: {data['impact']}")
            print("-" * 40)
            print(f"{Fore.GREEN}✨ DockDesk Auto-Fix Suggestion:")
            print(f"{Fore.CYAN}{data['suggested_fix']}")
            print("-" * 40)
            sys.exit(1)
        else:
            print(f"{Fore.GREEN}✅ KNOWLEDGE INTEGRITY VERIFIED")
            sys.exit(0)

    except Exception as e:
        print(f"{Fore.RED}Error parsing AI response: {e}")
        # Fallback print just in case
        try:
            print(response.text)
        except:
            pass

if __name__ == "__main__":
    run_audit("auth.py", "README.md")
