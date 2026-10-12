import json
from pathlib import Path
from services.pipeline import build_document
from services.summary import generate_summary

raw = json.loads((Path(__file__).resolve().parent.parent / "samples" / "cbc_sample.json").read_text(encoding="utf-8"))
doc = build_document(raw, "cbc_sample.pdf")
print(json.dumps(generate_summary(doc), indent=2, ensure_ascii=False))