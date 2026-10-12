import io
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

PROMPT = """You are a medical document data extractor.
Read the document and return ONLY valid JSON in exactly this shape:
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


def _pdf_text(file_bytes: bytes) -> str:
    import pdfplumber
    parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def _extract_groq(text: str) -> dict:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=60)
    model = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
    last_error = None
    for round_number in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": "Document text:\n\n" + text[:30000]},
                ],
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            last_error = e
            print(f"Groq {model} failed: {str(e)[:150]}")
            time.sleep(3 * (round_number + 1))
    raise RuntimeError(f"Groq extraction failed: {last_error}")


def _extract_gemini(file_bytes: bytes, mime_type: str) -> dict:
    # Imported here so the app runs without google-genai installed.
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(timeout=120000),
    )
    models = [m.strip() for m in os.getenv("GEMINI_MODELS", os.getenv("GEMINI_MODEL", "")).split(",") if m.strip()]
    last_error = None
    for round_number in range(3):
        for model in models:
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
                print(f"{model} failed: {str(e)[:120]}")
        time.sleep(5 * (round_number + 1))
    raise RuntimeError(f"Extraction failed: {last_error}")


import base64

def _extract_groq_vision(file_bytes: bytes, mime_type: str) -> dict:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=90)
    model = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    images = []  # list of (bytes, mime)
    if mime_type == "application/pdf":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:2]:
                buf = io.BytesIO()
                page.to_image(resolution=150).original.save(buf, format="PNG")
                images.append((buf.getvalue(), "image/png"))
    else:
        images.append((file_bytes, mime_type))

    content = [{"type": "text", "text": PROMPT}]
    for data, mt in images:
        b64 = base64.b64encode(data).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{mt};base64,{b64}"}})

    last_error = None
    for round_number in range(2):
        try:
            r = client.chat.completions.create(
                model=model, temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": content}],
            )
            return json.loads(r.choices[0].message.content)
        except Exception as e:
            last_error = e
            print(f"Groq vision {model} failed: {str(e)[:150]}")
            time.sleep(3)
    raise RuntimeError(f"Groq vision failed: {last_error}")

def extract_document(file_bytes: bytes, mime_type: str) -> dict:
    use_gemini = os.getenv("USE_GEMINI", "false").strip().lower() == "true"
    if use_gemini:
        return _extract_gemini(file_bytes, mime_type)

    text = ""
    if mime_type == "application/pdf":
        text = _pdf_text(file_bytes)
    elif mime_type.startswith("text/"):
        text = file_bytes.decode("utf-8", errors="ignore")

    if text:
        return _extract_groq(text)

    
    return _extract_groq_vision(file_bytes, mime_type)