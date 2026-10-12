from services.pipeline import build_document
from services.fhir import build_bundle

RAW = {
    "doc_type": "lab_report",
    "doc_date": "2026-03-14",
    "observations": [{"test": "Hemoglobin", "value": 11.2, "unit": "g/dL",
                      "ref_low": 13.0, "ref_high": 17.0, "confidence": 1.0,
                      "source_text": "Hemoglobin 11.2 g/dL 13.0 - 17.0"}],
    "medications": [{"drug": "Metformin", "dose": "500 mg", "frequency": "twice daily",
                     "duration": "30 days", "confidence": 1.0, "source_text": "x"}],
    "conditions": [{"name": "anemia", "date": None, "source_text": "x"}],
}


def test_bundle_has_all_resource_types():
    doc = build_document(RAW, "x.pdf")
    bundle = build_bundle([doc], {"name": "Demo Patient", "abha_id": "91-1234-5678-9012"})
    types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    assert bundle["resourceType"] == "Bundle"
    for t in ("Patient", "DocumentReference", "DiagnosticReport",
              "Observation", "MedicationRequest", "Condition"):
        assert t in types


def test_low_hemoglobin_is_marked_L_and_abha_present():
    doc = build_document(RAW, "x.pdf")
    bundle = build_bundle([doc], {"name": "Demo Patient", "abha_id": "91-1234-5678-9012"})
    resources = [e["resource"] for e in bundle["entry"]]
    obs = [r for r in resources if r["resourceType"] == "Observation"][0]
    patient = [r for r in resources if r["resourceType"] == "Patient"][0]
    assert obs["interpretation"][0]["coding"][0]["code"] == "L"
    assert patient["identifier"][0]["value"] == "91-1234-5678-9012"