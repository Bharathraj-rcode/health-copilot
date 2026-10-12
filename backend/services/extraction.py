import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROMPT = """You are a medical document data extractor.
Read the attached document and return ONLY valid JSON in exactly this shape:
{
  "doc_type": "lab_report | prescription | discharge_summary | other",
  "doc_date": "YYYY-MM-DD or null",
  "observations": [
    {"test": "", "value": 0, "unit": "", "ref_low": null, "ref_high": null,
     "confidence": 0.0, "source_text": ""}
  ],
  "medications": [
    {"drug": "", "dose": "", "frequency": "", "duration": "",
     "confidence": 0.0, "source_text": ""}
  ],
  "conditions": [
    {"name": "", "date": null, "source_text": ""}
  ]
}
Rules:
- Copy values exactly as printed. Never guess. If unreadable, use null.
- value must be a number. Reference range numbers go in ref_low and ref_high.
- source_text is the exact line from the document the item came from.
- confidence is 0 to 1 (how sure you are you read it correctly).
- Do NOT decide whether a value is high or low. Do NOT add medical advice.
- Dates must be YYYY-MM-DD.
"""


def extract_document(file_bytes: bytes, mime_type: str) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    last_error = None
    for _attempt in range(2):  # try once, retry once if it fails
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    PROMPT,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Extraction failed: {last_error}")