import json
from services.extraction import PROMPT
from services.fallback import extract_with_groq

with open("D:/HacXL/health-copilot/samples/cbc_sample.pdf", "rb") as f:
    data = extract_with_groq(f.read(), "application/pdf", PROMPT)

print(json.dumps(data, indent=2))