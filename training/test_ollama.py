# test_ollama.py
"""Diagnostics script to inspect raw JSON output from local Ollama API."""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:26b"

def run_test():
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": "你好，請隨便回覆我五個字。"}
        ],
        "stream": False
    }
    try:
        print(f"Sending request to {OLLAMA_URL} with model {MODEL_NAME}...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        print(f"HTTP Status Code: {response.status_code}")
        print("Raw JSON Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    run_test()
