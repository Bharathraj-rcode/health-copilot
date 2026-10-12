
import json
from pathlib import Path

from services.extraction import extract_document

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def norm(s):
    return (s or "").strip().lower()


def same_number(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return False


def main():
    total = correct = 0
    for pdf in sorted(SAMPLES.glob("*.pdf")):
        truth_file = pdf.with_suffix(".json")
        if not truth_file.exists():
            continue
        truth = json.loads(truth_file.read_text(encoding="utf-8"))
        got = extract_document(pdf.read_bytes(), "application/pdf")
        got_obs = {norm(o.get("test")): o for o in got.get("observations", [])}
        print(f"\n{pdf.name}")
        for exp in truth["observations"]:
            total += 1
            g = got_obs.get(norm(exp["test"]))
            if g is not None and same_number(g.get("value"), exp["value"]):
                correct += 1
                print(f"  OK    {exp['test']} = {exp['value']}")
            else:
                found = g.get("value") if g else "missing"
                print(f"  FAIL  {exp['test']}: expected {exp['value']}, got {found}")
    pct = round(100 * correct / total, 1) if total else 0
    print(f"\nSCORE: {correct}/{total} ({pct}%)")


if __name__ == "__main__":
    main()