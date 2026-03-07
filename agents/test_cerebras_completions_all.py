import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY_1"))

models_to_try = [
    "qwen-3-235b-a22b-instruct-2507",
    "gpt-oss-120b",
    "zai-glm-4.7",
    "llama3.1-8b"
]

for model in models_to_try:
    try:
        print(f"Trying {model}...")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=10
        )
        print(f"  Success: {response.choices[0].message.content}")
    except Exception as e:
        print(f"  Error: {e}")
