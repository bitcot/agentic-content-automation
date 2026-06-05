import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
models = client.models.list()
for m in models.data:
    if "dall" in m.id.lower() or "image" in m.id.lower():
        print(m.id)
print("Done.")
