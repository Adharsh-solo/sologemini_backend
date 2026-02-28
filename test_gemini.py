import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(r"c:\Users\Adharsh PB\OneDrive\Desktop\projects\geminiclone\sologemini_backend\.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.5-flash')
history = [{'role': 'user', 'parts': [{'text': 'hi'}]}, {'role': 'model', 'parts': [{'text': 'hello'}]}]
try:
    chat = model.start_chat(history=history)
    resp = chat.send_message("what is the weather")
    print("SUCCESS", resp.text)
except Exception as e:
    import traceback
    print("ERROR", str(e))
    traceback.print_exc()
