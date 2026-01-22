# app/core/learning_memory.py
import sqlite3
import threading
from typing import Dict, Optional, List

DB_PATH = "data/learning_memory.db"
_init_lock = threading.Lock()

def _ensure_db():
    with _init_lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE,
            status TEXT DEFAULT 'unknown',
            times_asked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            action TEXT,
            info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

def record_unknown_question(question: str):
    _ensure_db()
    q = question.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM questions WHERE question = ?", (q,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE questions SET times_asked = times_asked + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (row[0],))
        qid = row[0]
    else:
        cur.execute("INSERT INTO questions(question, status, times_asked) VALUES (?, 'unknown', 1)", (q,))
        qid = cur.lastrowid
    cur.execute("INSERT INTO audit(question_id, action, info) VALUES (?, 'record_unknown', '')", (qid,))
    conn.commit()
    conn.close()
    return qid

def mark_question_learned(question: str):
    _ensure_db()
    q = question.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM questions WHERE question = ?", (q,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE questions SET status = 'learned', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (row[0],))
        qid = row[0]
    else:
        cur.execute("INSERT INTO questions(question, status, times_asked, updated_at) VALUES (?, 'learned', 0, CURRENT_TIMESTAMP)", (q,))
        qid = cur.lastrowid
    cur.execute("INSERT INTO audit(question_id, action, info) VALUES (?, 'mark_learned', '')", (qid,))
    conn.commit()
    conn.close()
    return qid

def get_unknowns(limit: int = 100) -> List[Dict]:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id,question,times_asked FROM questions WHERE status='unknown' ORDER BY times_asked DESC LIMIT ?", (limit,))
    rows = [{"id": r[0], "question": r[1], "times_asked": r[2]} for r in cur.fetchall()]
    conn.close()
    return rows
