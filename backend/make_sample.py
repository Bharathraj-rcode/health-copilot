from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

os.makedirs("../samples", exist_ok=True)
c = canvas.Canvas("../samples/cbc_sample.pdf", pagesize=A4)
y = 800
lines = [
    "SUNRISE DIAGNOSTICS LAB (SYNTHETIC SAMPLE)",
    "Patient: Demo Patient    Age/Sex: 45 / M",
    "Report Date: 14-03-2026",
    "",
    "Test                 Result     Unit       Reference Range",
    "Hemoglobin           11.2       g/dL       13.0 - 17.0",
    "WBC Count            7800       /cumm      4000 - 11000",
    "Platelet Count       150000     /cumm      150000 - 410000",
    "Fasting Glucose      142        mg/dL      70 - 100",
    "HbA1c                7.4        %          4.0 - 5.6",
    "",
    "Impression: Findings suggest anemia and raised blood sugar.",
    "Advice: Metformin 500 mg twice daily for 30 days.",
]
for line in lines:
    c.drawString(50, y, line)
    y -= 22
c.save()
print("Created ../samples/cbc_sample.pdf")