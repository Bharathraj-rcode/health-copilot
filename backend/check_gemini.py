import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = os.getenv("GEMINI_MODEL")
print("Using model:", model)

print("\nModels your key can use (flash ones):")
for m in client.models.list():
    if "flash" in m.name:
        print(" ", m.name)

print("\nTest answer:")
r = client.models.generate_content(model=model, contents="Say hello in one word.")
print(r.text)