
PATIENT_ID = "patient-1"
ABHA_SYSTEM = "https://healthid.ndhm.gov.in"
INTERP_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"
LOINC = "http://loinc.org"
INTERP = {"high": ("H", "High"), "low": ("L", "Low"), "normal": ("N", "Normal")}


LOINC_MAP = [
    # Diabetes / glucose
    (("hba1c", "glycated", "glycosylated"), "4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood"),
    (("fasting glucose", "fasting blood sugar", "fbs"), "1558-6", "Fasting glucose"),
    (("random glucose", "random blood sugar", "rbs"), "2345-7", "Glucose [Mass/volume] in Serum or Plasma"),

    # Complete blood count (specific names before general ones)
    (("mchc",), "786-4", "MCHC [Mass/volume]"),
    (("mch",), "785-6", "MCH [Entitic mass]"),
    (("mcv",), "787-2", "MCV [Entitic volume]"),
    (("rdw-cv", "rdw cv", "rdw"), "788-0", "Erythrocyte distribution width [Ratio]"),
    (("rdw-sd", "rdw sd"), "21000-5", "Erythrocyte distribution width [Entitic volume]"),
    (("hemoglobin", "haemoglobin"), "718-7", "Hemoglobin [Mass/volume] in Blood"),
    (("rbc", "red blood", "erythrocyte count"), "789-8", "Erythrocytes [#/volume] in Blood"),
    (("hct", "hematocrit", "haematocrit", "pcv"), "4544-3", "Hematocrit [Volume Fraction] of Blood"),
    (("wbc", "white blood", "leukocyte"), "6690-2", "Leukocytes [#/volume] in Blood"),
    (("neu%", "neutrophils %", "neutrophil %"), "770-8", "Neutrophils/100 leukocytes"),
    (("lym%", "lymphocytes %", "lymphocyte %"), "736-9", "Lymphocytes/100 leukocytes"),
    (("mon%", "monocytes %", "monocyte %"), "5905-5", "Monocytes/100 leukocytes"),
    (("eos%", "eosinophils %", "eosinophil %"), "713-8", "Eosinophils/100 leukocytes"),
    (("bas%", "basophils %", "basophil %"), "706-2", "Basophils/100 leukocytes"),
    (("lym#", "lymphocytes #", "lymphocyte count"), "731-0", "Lymphocytes [#/volume] in Blood"),
    (("plt", "platelet"), "777-3", "Platelets [#/volume] in Blood"),
    (("esr", "sedimentation"), "4537-7", "Erythrocyte sedimentation rate"),

    # Lipids
    (("ldl",), "13457-7", "LDL cholesterol"),
    (("hdl",), "2085-9", "HDL cholesterol"),
    (("vldl",), "13458-5", "VLDL cholesterol"),
    (("total cholesterol", "cholesterol, total"), "2093-3", "Cholesterol [Mass/volume] in Serum or Plasma"),
    (("triglyceride",), "2571-8", "Triglycerides"),

    # Kidney
    (("creatinine",), "2160-0", "Creatinine [Mass/volume] in Serum or Plasma"),
    (("blood urea nitrogen", "bun"), "3094-0", "Urea nitrogen [Mass/volume] in Serum or Plasma"),
    (("uric acid",), "3084-1", "Uric acid [Mass/volume] in Serum or Plasma"),

    # Electrolytes
    (("sodium",), "2951-2", "Sodium [Moles/volume] in Serum or Plasma"),
    (("potassium",), "2823-3", "Potassium [Moles/volume] in Serum or Plasma"),
    (("calcium",), "17861-6", "Calcium [Mass/volume] in Serum or Plasma"),

    # Liver
    (("sgpt", "alanine"), "1742-6", "Alanine aminotransferase"),
    (("sgot", "aspartate"), "1920-8", "Aspartate aminotransferase"),
    (("alkaline phosphatase",), "6768-6", "Alkaline phosphatase"),
    (("bilirubin",), "1975-2", "Bilirubin.total"),
    (("albumin",), "1751-7", "Albumin [Mass/volume] in Serum or Plasma"),

    # Thyroid and others
    (("tsh",), "3016-3", "Thyrotropin [Units/volume] in Serum or Plasma"),
    (("free t4", "ft4"), "3024-7", "Thyroxine (T4) free"),
    (("crp", "c-reactive", "c reactive"), "1988-5", "C reactive protein"),
    (("ferritin",), "2276-4", "Ferritin [Mass/volume] in Serum or Plasma"),
    (("vitamin b12", "b12"), "2132-9", "Vitamin B12 [Mass/volume] in Serum or Plasma"),
]


def _code(test):
    name = (test or "").lower()
    code = {"text": test}
    for keywords, loinc, display in LOINC_MAP:
        if any(k in name for k in keywords):
            code["coding"] = [{"system": LOINC, "code": loinc, "display": display}]
            break
    return code


def _ref(resource_type, rid):
    return {"reference": f"{resource_type}/{rid}"}


def _patient(patient):
    return {
        "resourceType": "Patient",
        "id": PATIENT_ID,
        "identifier": [{"system": ABHA_SYSTEM, "value": patient.get("abha_id", "")}],
        "name": [{"text": patient.get("name", "Demo Patient")}],
    }


def _observation(doc, o):
    res = {
        "resourceType": "Observation",
        "id": f"{doc['id']}-{o['id']}",
        "status": "final",
        "category": [{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "laboratory"}]}],
        "code": _code(o["test"]),
        "subject": _ref("Patient", PATIENT_ID),
    }
    if doc.get("doc_date"):
        res["effectiveDateTime"] = doc["doc_date"]
    if o["value"] is not None:
        res["valueQuantity"] = {"value": o["value"], "unit": o["unit"]}
    else:
        res["dataAbsentReason"] = {"text": "Value could not be read from the document"}
    if o["flag"] in INTERP:
        code, display = INTERP[o["flag"]]
        res["interpretation"] = [{"coding": [{"system": INTERP_SYSTEM, "code": code, "display": display}]}]
    if o["ref_low"] is not None or o["ref_high"] is not None:
        rng = {}
        if o["ref_low"] is not None:
            rng["low"] = {"value": o["ref_low"], "unit": o["unit"]}
        if o["ref_high"] is not None:
            rng["high"] = {"value": o["ref_high"], "unit": o["unit"]}
        res["referenceRange"] = [rng]
    if o.get("source_text"):
        res["note"] = [{"text": "Source: " + o["source_text"]}]
    return res


def _medication(doc, m):
    dose_text = " ".join(x for x in (m["dose"], m["frequency"], m["duration"]) if x)
    res = {
        "resourceType": "MedicationRequest",
        "id": f"{doc['id']}-{m['id']}",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {"text": m["drug"]},
        "subject": _ref("Patient", PATIENT_ID),
        "dosageInstruction": [{"text": dose_text}] if dose_text else [],
    }
    if doc.get("doc_date"):
        res["authoredOn"] = doc["doc_date"]
    return res


def _condition(doc, c):
    res = {
        "resourceType": "Condition",
        "id": f"{doc['id']}-{c['id']}",
        "code": {"text": c["name"]},
        "subject": _ref("Patient", PATIENT_ID),
    }
    when = c.get("date") or doc.get("doc_date")
    if when:
        res["recordedDate"] = when
    return res


def doc_resources(doc):
    resources = []
    docref = {
        "resourceType": "DocumentReference",
        "id": doc["id"],
        "status": "current",
        "type": {"text": doc["doc_type"]},
        "subject": _ref("Patient", PATIENT_ID),
        "content": [{"attachment": {"title": doc["filename"]}}],
    }
    if doc.get("doc_date"):
        docref["date"] = doc["doc_date"]
    resources.append(docref)

    observations = [_observation(doc, o) for o in doc["observations"]]
    if observations:
        report = {
            "resourceType": "DiagnosticReport",
            "id": doc["id"] + "-report",
            "status": "final",
            "code": {"text": doc["doc_type"]},
            "subject": _ref("Patient", PATIENT_ID),
            "result": [_ref("Observation", ob["id"]) for ob in observations],
        }
        if doc.get("doc_date"):
            report["effectiveDateTime"] = doc["doc_date"]
        resources.append(report)
        resources.extend(observations)

    resources.extend(_medication(doc, m) for m in doc["medications"])
    resources.extend(_condition(doc, c) for c in doc["conditions"])
    return resources


def build_bundle(docs, patient):
    resources = [_patient(patient)]
    for doc in docs:
        resources.extend(doc_resources(doc))
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"fullUrl": f"{r['resourceType']}/{r['id']}", "resource": r} for r in resources],
    }