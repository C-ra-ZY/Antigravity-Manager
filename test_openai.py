"""
测试 OpenAI 协议的非 Stream 请求自动转换
"""
from openai import OpenAI
import sys

BASE_URL = "http://127.0.0.1:8045/v1"
API_KEY = "sk-7fd8d437a64b4bf8b011fb17945a109d"

print(f"Initializing OpenAI client with:")
print(f"  Base URL: {BASE_URL}")
print(f"  API Key:  {API_KEY[:10]}...")

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def test_openai_non_stream():
    print(f"\n" + "="*50)
    print(f"Testing OpenAI Protocol (Non-Stream)")
    print("="*50)
    try:
        print("Sending request with STREAM=FALSE...")
        response = client.chat.completions.create(
            model="gpt-4",  # 会被映射到 gemini-2.5-pro
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello! Just checking connectivity."}]
        )
        
        print("✅ Success! Response:")
        print(f"  {response.choices[0].message.content}")
        print(f"  Model: {response.model}")
        print(f"  Tokens: {response.usage.total_tokens}")
    except Exception as e:
        print(f"❌ Error occurred:")
        print(f"  {str(e)}")

if __name__ == "__main__":
    test_openai_non_stream()
