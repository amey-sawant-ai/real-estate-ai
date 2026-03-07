from cerebras.cloud.sdk import Cerebras
import os
from dotenv import load_dotenv

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY_1"))
models = client.models.list()
for model in models.data:
    print(model.id)
