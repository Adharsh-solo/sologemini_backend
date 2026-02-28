import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(r"c:\Users\Adharsh PB\OneDrive\Desktop\projects\geminiclone\sologemini_backend\.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
