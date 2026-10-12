from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "samples"
OUT.mkdir(exist_ok=True)

DOCS = {
    "lipid_sample": [
        "CITY CARE DIAGNOSTICS (SYNTHETIC SAMPLE)",
        "Patient: Demo Patient    Age/Sex: 52 / F",
        "Collected: 02-04-2026",
        "",
        "LIPID PROFILE",
        "Total Cholesterol      238     mg/dL     < 200",
        "LDL Cholesterol        162     mg/dL     < 100",
        "HDL Cholesterol        38      mg/dL     > 40",
        "Triglycerides          190     mg/dL     < 150",
        "THYROID",
        "TSH                    2.1     uIU/mL    0.4 - 4.0",
        "OTHER",
        "Vitamin D              18      ng/mL",
    ],
    "prescription_sample": [
        "DR. A. KUMAR, MBBS, MD (SYNTHETIC SAMPLE)",
        "Patient: Demo Patient    Date: 02-04-2026",
        "Diagnosis: Hypertension",
        "",
        "Rx",
        "1. Tab Amlodipine 5 mg - once daily - 30 days",
        "2. Tab Atorvastatin 10 mg - at night - 30 days",
        "3. Cap Omeprazole 20 mg - before breakfast - 14 days",
        "",
        "Review after 4 weeks.",
    ],
    "discharge_sample": [
        "GREEN VALLEY HOSPITAL - DISCHARGE SUMMARY (SYNTHETIC SAMPLE)",
        "Patient: Demo Patient    Age/Sex: 61 / M",
        "Admitted: 10-03-2026    Discharged: 14-03-2026",
        "",
        "Diagnosis: Community acquired pneumonia; Type 2 diabetes mellitus",
        "",
        "Key results:",
        "WBC Count              15200   /cumm     4000 - 11000",
        "CRP                    48      mg/L      < 5",
        "",
        "Medicines at discharge:",
        "Tab Azithromycin 500 mg - once daily - 3 days",
        "Tab Paracetamol 650 mg - three times daily if fever - 5 days",
    ],
}

for name, lines in DOCS.items():
    c = canvas.Canvas(str(OUT / f"{name}.pdf"), pagesize=A4)
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    print("created", name + ".pdf")  