import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API Key")
    exit(1)

client = genai.Client(api_key=api_key)
try:
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(e)
