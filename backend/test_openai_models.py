import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
try:
    print("Testing dall-e-2")
    res = client.images.generate(model="dall-e-2", prompt="a tiny cat", n=1, size="256x256")
    print("dall-e-2 success:", res.data[0].url)
except Exception as e:
    print("dall-e-2 error:", e)

try:
    print("Testing dall-e-3")
    res = client.images.generate(model="dall-e-3", prompt="a tiny dog", n=1, size="1024x1024")
    print("dall-e-3 success:", res.data[0].url)
except Exception as e:
    print("dall-e-3 error:", e)
