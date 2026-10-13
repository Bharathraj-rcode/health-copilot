import os
import json
from dotenv import load_dotenv

load_dotenv()

DISCLAIMER = "Not medical advice. Please consult your doctor."
TAMIL_UNAVAILABLE = "தமிழ் சுருக்கம் தற்போது கிடைக்கவில்லை. தயவுசெய்து சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்."

RULES = """You write a patient-friendly summary of medical document data.
You are given ONLY structured facts. The High/Low/Normal flags were already
decided by software. Do not change them and do not decide abnormality yourself.

Return ONLY valid JSON in exactly this shape:
{
  "summary_en": "",
  "summary_ta": "",
  "questions_en": ["", ""],
  "questions_ta": ["", ""]
}

Rules:
- Write for a person with no medical background. Short sentences, simple words.
- summary_en is 4 to 7 sentences. Mention each abnormal (high or low) value
  with what it GENERALLY can mean, using words like "may indicate" or "can be
  linked to". Briefly say what is normal too.
- NEVER diagnose. NEVER say the person has a disease. NEVER recommend, start,
  stop or change any medicine or dose. For medicines, only say what the report
  lists and that the doctor decides about them.
- Do not name specific diseases or deficiencies (for example anemia or iron deficiency).
  Say only that a value is lower or higher than the reference range and that the doctor
  will explain possible reasons.
- questions_en must be specific to the abnormal values. Do not ask whether to discuss
  something with the doctor, and do not ask about treatment.
- If a value says needs_review, tell the reader to double-check it against the
  original report.
- If a flag is "unknown", say there was no reference range to compare with.
- Do not invent any value or fact that is not in the facts below.
- questions_en: 3 to 5 short questions the person could ask their doctor.
- summary_ta and questions_ta: the same content in simple, natural spoken
  Tamil (Tamil script). Keep test names and medicine names in English letters.
"""


def _facts(doc):
    lines = [f"Document type: {doc['doc_type']}", f"Date: {doc.get('doc_date') or 'unknown'}", "", "Lab values:"]
    for o in doc["observations"]:
        rng = ""
        if o["ref_low"] is not None or o["ref_high"] is not None:
            rng = f", reference {o['ref_low']} to {o['ref_high']}"
        review = " (needs_review)" if o["needs_review"] else ""
        lines.append(f"- {o['test']}: {o['value']} {o['unit']}{rng}. Flag: {o['flag']}{review}")
    lines.append("")
    lines.append("Medicines listed:")
    for m in doc["medications"]:
        lines.append(f"- {m['drug']} {m['dose']}, {m['frequency']}, {m['duration']}")
    lines.append("")
    lines.append("Conditions mentioned in the report:")
    for c in doc["conditions"]:
        lines.append(f"- {c['name']}")
    return "\n".join(lines)


def _call_gemini(prompt):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),
                          http_options=types.HttpOptions(timeout=60000))
    models = os.getenv("GEMINI_MODELS", os.getenv("GEMINI_MODEL", "")).split(",")
    r = client.models.generate_content(
        model=models[0].strip(), contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2))
    return json.loads(r.text)


def _call_groq(prompt):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    r = client.chat.completions.create(
        model=os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b"),
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}, temperature=0.2)
    return json.loads(r.choices[0].message.content)


def _call_llm(prompt):
    use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
    attempts = ([_call_gemini] if use_gemini else []) + ([_call_groq] if os.getenv("GROQ_API_KEY") else [])
    last = None
    for fn in attempts:
        for _ in range(2):
            try:
                return fn(prompt)
            except Exception as e:
                last = e
                print(f"Summary call failed ({fn.__name__}): {str(e)[:120]}")
    raise RuntimeError(f"All summary calls failed: {last}")


def _clean_list(items):
    if not isinstance(items, list):
        return []
    return [str(x).strip() for x in items if str(x).strip()][:5]


def _fallback_english(doc):
    abnormal = [o for o in doc["observations"] if o["flag"] in ("high", "low")]
    if not abnormal:
        return "The values we could read are within their reference ranges, or have no range to compare with. Please read the original report too."
    parts = [f"{o['test']} is {o['flag']} ({o['value']} {o['unit']})" for o in abnormal]
    return ("Some values are outside their reference ranges: " + "; ".join(parts) +
            ". Please discuss these results with your doctor.")


def generate_summary(doc):
    summary = {
        "en": _fallback_english(doc),
        "ta": TAMIL_UNAVAILABLE,
        "questions_for_doctor": {"en": ["What do these results mean for me?",
                                        "Do I need any follow-up tests?"], "ta": []},
        "disclaimer": DISCLAIMER,
    }
    try:
        data = _call_llm(RULES + "\nFACTS:\n" + _facts(doc))
        if isinstance(data.get("summary_en"), str) and data["summary_en"].strip():
            summary["en"] = data["summary_en"].strip()
        if isinstance(data.get("summary_ta"), str) and data["summary_ta"].strip():
            summary["ta"] = data["summary_ta"].strip()
        qe, qt = _clean_list(data.get("questions_en")), _clean_list(data.get("questions_ta"))
        if qe:
            summary["questions_for_doctor"]["en"] = qe
        summary["questions_for_doctor"]["ta"] = qt
    except Exception as e:
        print("Summary generation failed, using fallback:", e)
    return summary