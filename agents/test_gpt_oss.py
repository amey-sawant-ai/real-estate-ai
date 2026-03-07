import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY_1"))

try:
    print("Trying gpt-oss-120b with longer prompt...")
    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": "Tell me a joke about real estate."}],
        max_tokens=50
    )
    print(f"Content: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")
