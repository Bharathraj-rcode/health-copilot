import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "health.db"
DEFAULT_ABHA = "91-1234-5678-9012"  # mock ID, no real ABDM call


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS documents ("
        "id TEXT PRIMARY KEY, file_hash TEXT, data TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS patient (id INTEGER PRIMARY KEY, abha_id TEXT)")
    conn.execute("INSERT OR IGNORE INTO patient (id, abha_id) VALUES (1, ?)", (DEFAULT_ABHA,))
    conn.commit()
    conn.close()


def save_document(doc, file_hash):
    conn = _connect()
    conn.execute(
        "INSERT INTO documents (id, file_hash, data, created_at) VALUES (?, ?, ?, ?)",
        (doc["id"], file_hash, json.dumps(doc), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_document(doc_id):
    conn = _connect()
    row = conn.execute("SELECT data FROM documents WHERE id = ?", (doc_id,)).fetchone()
    conn.close()
    return json.loads(row["data"]) if row else None


def get_by_hash(file_hash):
    conn = _connect()
    row = conn.execute("SELECT data FROM documents WHERE file_hash = ?", (file_hash,)).fetchone()
    conn.close()
    return json.loads(row["data"]) if row else None


def list_documents():
    conn = _connect()
    rows = conn.execute("SELECT data FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()
    return [json.loads(r["data"]) for r in rows]


def get_patient():
    conn = _connect()
    row = conn.execute("SELECT abha_id FROM patient WHERE id = 1").fetchone()
    conn.close()
    return {"name": "Demo Patient", "abha_id": row["abha_id"] if row else DEFAULT_ABHA}


def set_abha(abha_id):
    conn = _connect()
    conn.execute("UPDATE patient SET abha_id = ? WHERE id = 1", (abha_id,))
    conn.commit()
    conn.close()