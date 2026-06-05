import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
try:
    res = client.images.generate(model="gpt-image-1-mini", prompt="test", n=1, size="1024x1024")
    with open("test_output.txt", "w") as f:
        f.write(str(res))
except Exception as e:
    with open("test_output.txt", "w") as f:
        f.write("FAILED: " + str(e))
