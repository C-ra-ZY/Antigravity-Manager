from anthropic import Anthropic
import sys

# Define constants
BASE_URL = "http://127.0.0.1:8045"
API_KEY = "sk-7fd8d437a64b4bf8b011fb17945a109d"

print(f"Initializing Anthropic client with:")
print(f"  Base URL: {BASE_URL}")
print(f"  API Key:  {API_KEY[:10]}...")

client = Anthropic(
    base_url=BASE_URL,
    api_key=API_KEY
)

def run_test(model_name):
    print(f"\n" + "="*50)
    print(f"Testing Model: {model_name}")
    print("="*50)
    try:
        print("Sending request with STREAM=FALSE (testing auto-conversion)...")
        # 使用非 Stream 模式测试自动转换
        response = client.messages.create(
            model=model_name,
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello! Just checking connectivity."}]
        )
        
        print("✅ Success! Response:")
        print(f"  {response.content[0].text}")
    except Exception as e:
        print(f"❌ Error occurred:")
        print(f"  {str(e)}")

if __name__ == "__main__":
    # 只测试 Opus 模型
    run_test("claude-opus-4-5-thinking")

