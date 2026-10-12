import os
import io
import json
import base64
import pdfplumber
from groq import Groq


def extract_with_groq(file_bytes: bytes, mime_type: str, prompt: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    if mime_type == "application/pdf":
        # Digital PDFs: read the text directly, then send the text to the model
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        if not text.strip():
            raise RuntimeError("This PDF is a scan with no text. Upload it as an image instead.")
        model = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")
        messages = [{"role": "user", "content": prompt + "\n\nDOCUMENT TEXT:\n" + text}]
    else:
        # Photos and scans: send the image to a vision model
        b64 = base64.b64encode(file_bytes).decode()
        model = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
            ],
        }]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)