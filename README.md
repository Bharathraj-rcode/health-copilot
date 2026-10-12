# Health Copilot
AI-powered personal health copilot (HacXLerate 2026 Round 1).

## Structure
- backend/   Python FastAPI API
- frontend/  React website
- samples/   synthetic test reports
- docs/      architecture diagram and slides

## Run backend
cd backend
python -m venv venv
venv\\Scripts\\activate      (Windows)  |  source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
copy .env.example to .env and add your key
uvicorn main:app --reload
