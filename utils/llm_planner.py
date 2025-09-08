import os
import requests
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

API_KEYS = [os.getenv("GROQ_API_KEY_1"), os.getenv("GROQ_API_KEY_2")]
MODEL_NAME = os.getenv("MODEL_NAME", "mixtral-8x7b-32768")  # Optional fallback
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# Rate limiting variables
last_request_time = 0
min_request_interval = 2  # Minimum 2 seconds between requests

def call_llm(prompt: str) -> str:
    global last_request_time
    
    # Rate limiting - wait if needed
    current_time = time.time()
    time_since_last = current_time - last_request_time
    if time_since_last < min_request_interval:
        wait_time = min_request_interval - time_since_last
        print(f"[LLMPlanner] ⏳ Rate limiting: waiting {wait_time:.1f}s...")
        time.sleep(wait_time)
    
    last_request_time = time.time()
    
    for key in API_KEYS:
        if not key:
            continue

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000  # Limit response length to avoid long processing
        }

        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 429:
                print(f"[LLMPlanner] ⏳ Rate limit hit, waiting 5 seconds...")
                time.sleep(5)
                continue
                
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            if "429" in str(e):
                print(f"[LLMPlanner] ⏳ Rate limit exceeded, trying next key...")
                time.sleep(3)
                continue
            print(f"[LLMPlanner] ⚠️ HTTP error with key: {key[:6]}... — {e}")
            continue
        except Exception as e:
            print(f"[LLMPlanner] ⚠️ Failed with key: {key[:6]}... — {e}")
            continue

    return "[LLMPlanner] ❌ Error: All API keys failed. Check .env or usage limits."

# Optional: Async wrapper if any agent uses it in asyncio tasks
async def llm_chat(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, call_llm, prompt)