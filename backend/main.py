import os
import re
import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

from services import storage
from services.pipeline import process_file, build_timeline

from services.fhir import build_bundle

storage.init_db()
app = FastAPI(title="Health Copilot API")

origins = ["http://localhost:5173"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
EXT_TO_MIME = {".pdf": "application/pdf", ".jpg": "image/jpeg",
               ".jpeg": "image/jpeg", ".png": "image/png"}
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def error(message, status):
    return JSONResponse({"error": message}, status_code=status)


def guess_mime(filename, content_type):
    ext = Path(filename or "").suffix.lower()
    if ext in EXT_TO_MIME:
        return EXT_TO_MIME[ext]
    return content_type if content_type in EXT_TO_MIME.values() else None


def run_pipeline(data, mime, filename, fallback_raw=None):
    try:
        return process_file(data, mime, filename, fallback_raw)
    except Exception as e:
        print("Processing failed:", e)
        return error("We could not read this document right now. "
                     "The AI service may be busy, please try again in a minute.", 502)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/documents")
def upload_document(file: UploadFile = File(...), lang: str = Form("en")):
    data = file.file.read()
    if not data:
        return error("The file is empty.", 400)
    if len(data) > MAX_BYTES:
        return error("File is too large. Please upload a file under 10 MB.", 413)
    mime = guess_mime(file.filename, file.content_type)
    if not mime:
        return error("Unsupported file type. Please upload a PDF, JPG or PNG.", 400)
    return run_pipeline(data, mime, file.filename or "upload")


@app.get("/api/documents")
def list_documents():
    return storage.list_documents()


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: str):
    doc = storage.get_document(doc_id)
    return doc if doc else error("Document not found.", 404)


@app.post("/api/samples/{name}")
def load_sample(name: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        return error("Unknown sample.", 404)
    pdf = SAMPLES_DIR / f"{name}.pdf"
    if not pdf.exists():
        return error("Unknown sample.", 404)
    saved = SAMPLES_DIR / f"{name}.json"  # optional pre-extracted backup
    fallback_raw = json.loads(saved.read_text(encoding="utf-8")) if saved.exists() else None
    return run_pipeline(pdf.read_bytes(), "application/pdf", pdf.name, fallback_raw)


@app.get("/api/timeline")
def timeline():
    return {"events": build_timeline(storage.list_documents())}


class PatientUpdate(BaseModel):
    abha_id: str


@app.get("/api/patient")
def get_patient():
    return storage.get_patient()


@app.put("/api/patient")
def update_patient(body: PatientUpdate):
    abha = body.abha_id.strip()
    if not abha or len(abha) > 30:
        return error("Please enter a valid ABHA ID.", 400)
    storage.set_abha(abha)
    return storage.get_patient()

@app.get("/api/fhir")
def fhir_all():
    bundle = build_bundle(storage.list_documents(), storage.get_patient())
    return JSONResponse(bundle, media_type="application/fhir+json")


@app.get("/api/documents/{doc_id}/fhir")
def fhir_one(doc_id: str):
    doc = storage.get_document(doc_id)
    if not doc:
        return error("Document not found.", 404)
    bundle = build_bundle([doc], storage.get_patient())
    return JSONResponse(bundle, media_type="application/fhir+json")