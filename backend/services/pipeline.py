import re
import uuid
import hashlib
from datetime import date

from services import storage
from services.extraction import extract_document
from services.flags import compute_flag, fallback_range
from services.summary import generate_summary

DISCLAIMER = "Not medical advice. Please consult your doctor."
DOC_TYPES = {"lab_report", "prescription", "discharge_summary", "other"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _num(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return None


def _date(v):
    return v if isinstance(v, str) and DATE_RE.match(v) else None


def _conf(v):
    n = _num(v)
    return 0.5 if n is None else max(0.0, min(1.0, float(n)))


def _fmt(v):
    if v is None:
        return ""
    return str(int(v)) if float(v).is_integer() else str(v)


def build_document(raw, filename):
    doc_date = _date(raw.get("doc_date"))
    observations, medications, conditions = [], [], []

    for i, o in enumerate(raw.get("observations") or [], start=1):
        value = _num(o.get("value"))
        low, high = _num(o.get("ref_low")), _num(o.get("ref_high"))
        if low is None and high is None:  # report printed no range -> use built-in
            builtin = fallback_range(o.get("test"))
            if builtin:
                low, high = builtin
        conf = _conf(o.get("confidence"))
        observations.append({
            "id": f"o{i}",
            "test": str(o.get("test") or "Unknown test"),
            "value": value,
            "unit": o.get("unit") or "",
            "ref_low": low,
            "ref_high": high,
            "flag": compute_flag(value, low, high),
            "confidence": conf,
            "needs_review": conf < 0.7 or value is None,
            "source_text": o.get("source_text") or "",
        })

    for i, m in enumerate(raw.get("medications") or [], start=1):
        if not m.get("drug"):
            continue
        conf = _conf(m.get("confidence"))
        medications.append({
            "id": f"m{i}",
            "drug": str(m["drug"]),
            "dose": m.get("dose") or "",
            "frequency": m.get("frequency") or "",
            "duration": m.get("duration") or "",
            "confidence": conf,
            "needs_review": conf < 0.7,
            "source_text": m.get("source_text") or "",
        })

    for i, c in enumerate(raw.get("conditions") or [], start=1):
        if not c.get("name"):
            continue
        conditions.append({
            "id": f"c{i}",
            "name": str(c["name"]),
            "date": _date(c.get("date")) or doc_date,
            "source_text": c.get("source_text") or "",
        })

    doc_type = raw.get("doc_type")
    return {
        "id": "doc_" + uuid.uuid4().hex[:8],
        "filename": filename,
        "doc_type": doc_type if doc_type in DOC_TYPES else "other",
        "doc_date": doc_date,
        "uploaded_at": date.today().isoformat(),
        "status": "done",
        "observations": observations,
        "medications": medications,
        "conditions": conditions,
        "summary": {
            "en": "",
            "ta": "",
            "questions_for_doctor": {"en": [], "ta": []},
            "disclaimer": DISCLAIMER,
        },
    }


def process_file(file_bytes, mime_type, filename, fallback_raw=None):
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    existing = storage.get_by_hash(file_hash)  # same file twice -> no second AI call
    if existing:
        return existing
    try:
        raw = extract_document(file_bytes, mime_type)
    except Exception:
        if fallback_raw is None:
            raise
        print("AI unavailable, using saved sample extraction")
        raw = fallback_raw
    doc = build_document(raw, filename)
    doc["summary"] = generate_summary(doc)
    storage.save_document(doc, file_hash)
    return doc


def _lab_detail(o):
    if o["value"] is None:
        return "Could not read this value, please verify"
    names = {"low": "Low", "high": "High", "normal": "Normal", "unknown": "No reference range"}
    text = names[o["flag"]]
    low, high = o["ref_low"], o["ref_high"]
    if low is not None and high is not None:
        text += f" (ref {_fmt(low)}-{_fmt(high)})"
    elif high is not None:
        text += f" (ref up to {_fmt(high)})"
    elif low is not None:
        text += f" (ref above {_fmt(low)})"
    return text


def build_timeline(docs):
    events = []
    for d in docs:
        when = d.get("doc_date") or d.get("uploaded_at")
        for o in d["observations"]:
            if o["value"] is None:
                title = f"{o['test']} (unreadable)"
            else:
                title = f"{o['test']} {_fmt(o['value'])} {o['unit']}".strip()
            events.append({"date": when, "type": "lab", "title": title,
                           "detail": _lab_detail(o), "flag": o["flag"], "document_id": d["id"]})
        for m in d["medications"]:
            events.append({"date": when, "type": "medication",
                           "title": f"{m['drug']} {m['dose']}".strip(),
                           "detail": ", ".join(x for x in (m["frequency"], m["duration"]) if x),
                           "flag": "unknown", "document_id": d["id"]})
        for c in d["conditions"]:
            events.append({"date": c["date"] or when, "type": "condition", "title": c["name"],
                           "detail": "Mentioned in the report", "flag": "unknown",
                           "document_id": d["id"]})
    events.sort(key=lambda e: e["date"] or "", reverse=True)
    return events