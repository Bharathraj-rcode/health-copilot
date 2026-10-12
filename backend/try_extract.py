import json
from services.extraction import extract_document

with open("../samples/cbc_sample.pdf", "rb") as f:
    data = extract_document(f.read(), "application/pdf")

print(json.dumps(data, indent=2))