"""Simple SQLite-backed storage for uploads and detection artifacts."""
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
import datetime
import pandas as pd

DB_PATH = Path("data/storage.db")


def init_db(db_path: Optional[Path] = None):
    db = DB_PATH if db_path is None else db_path
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            stored_at TEXT,
            filepath TEXT,
            detections_path TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_upload(filename: str, df: pd.DataFrame, detections: List[Dict]) -> int:
    """Save uploaded CSV and detections; record entry in DB and return upload id."""
    init_db()
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uploads_dir = Path("artifacts/uploads")
    detections_dir = Path("artifacts/detections")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    detections_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{ts}_{Path(filename).stem}.csv"
    stored_path = uploads_dir / stored_name
    df.to_csv(stored_path, index=False)

    det_name = f"{ts}_{Path(filename).stem}_detections.csv"
    det_path = detections_dir / det_name
    pd.DataFrame(detections).to_csv(det_path, index=False)

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute(
        "INSERT INTO uploads (filename, stored_at, filepath, detections_path) VALUES (?,?,?,?)",
        (filename, ts, str(stored_path), str(det_path)),
    )
    conn.commit()
    upload_id = c.lastrowid
    conn.close()
    return upload_id


def list_uploads(limit: int = 100) -> List[Dict]:
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT id, filename, stored_at, filepath, detections_path FROM uploads ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "filename": r[1], "stored_at": r[2], "filepath": r[3], "detections_path": r[4]} for r in rows
    ]


def get_upload(upload_id: int) -> Optional[Dict]:
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT id, filename, stored_at, filepath, detections_path FROM uploads WHERE id=?", (upload_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "filename": row[1], "stored_at": row[2], "filepath": row[3], "detections_path": row[4]}
