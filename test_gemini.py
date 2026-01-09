"""
测试 Gemini 协议的非 Stream 请求
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8045"
API_KEY = "sk-7fd8d437a64b4bf8b011fb17945a109d"

print(f"Testing Gemini Protocol (Non-Stream)")
print(f"  Base URL: {BASE_URL}")
print(f"  API Key:  {API_KEY[:10]}...")

def test_gemini_non_stream():
    print(f"\n" + "="*50)
    print(f"Testing Gemini Protocol (Non-Stream)")
    print("="*50)
    
    url = f"{BASE_URL}/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello! Just checking connectivity."
            }],
            "role": "user"
        }],
        "generationConfig": {
            "maxOutputTokens": 100
        }
    }
    
    try:
        print("Sending request with STREAM=FALSE...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            print("✅ Success! Response:")
            print(f"  {text}")
            print(f"  Status: {response.status_code}")
        else:
            print(f"❌ Error occurred:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"❌ Error occurred:")
        print(f"  {str(e)}")

if __name__ == "__main__":
    test_gemini_non_stream()
