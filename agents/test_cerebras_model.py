import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY_1"))

try:
    print("Trying qwen model...")
    response = client.chat.completions.create(
        model="qwen-3-235b-a22b-instruct-2507",
        messages=[{"role": "user", "content": "hello"}]
    )
    print(response.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("\nTrying llama small model...")
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": "hello"}]
    )
    print(response.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()
