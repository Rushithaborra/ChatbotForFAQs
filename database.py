import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "shopassist.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS feedback (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id  TEXT    NOT NULL,
            question    TEXT,
            answer      TEXT,
            category    TEXT,
            rating      INTEGER,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS custom_faqs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,
            question    TEXT    NOT NULL,
            answer      TEXT    NOT NULL,
            keywords    TEXT    DEFAULT '[]',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS escalations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT,
            user_name   TEXT,
            user_email  TEXT,
            issue       TEXT,
            status      TEXT    DEFAULT 'open',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );
        """)


# ── Feedback ──────────────────────────────────────────────────────────────────

def save_feedback(message_id: str, question: str, answer: str,
                  category: str, rating: int):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO feedback (message_id,question,answer,category,rating) "
            "VALUES (?,?,?,?,?)",
            (message_id, question, answer, category, rating),
        )


def get_feedback_stats():
    with _conn() as conn:
        rows = conn.execute("""
            SELECT category,
                   COUNT(*)                                          AS total,
                   SUM(CASE WHEN rating =  1 THEN 1 ELSE 0 END)     AS positive,
                   SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END)     AS negative
            FROM feedback
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_recent_feedback(limit: int = 20):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ── Custom FAQs ───────────────────────────────────────────────────────────────

def get_custom_faqs() -> list:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM custom_faqs ORDER BY category, question"
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["keywords"] = json.loads(d["keywords"]) if d["keywords"] else []
            result.append(d)
        return result


def add_custom_faq(category: str, question: str, answer: str, keywords: list):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO custom_faqs (category,question,answer,keywords) VALUES (?,?,?,?)",
            (category, question, answer, json.dumps(keywords)),
        )


def update_custom_faq(faq_id: int, category: str, question: str,
                       answer: str, keywords: list):
    with _conn() as conn:
        conn.execute(
            "UPDATE custom_faqs SET category=?,question=?,answer=?,keywords=?,"
            "updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (category, question, answer, json.dumps(keywords), faq_id),
        )


def delete_custom_faq(faq_id: int):
    with _conn() as conn:
        conn.execute("DELETE FROM custom_faqs WHERE id=?", (faq_id,))


# ── Escalations ───────────────────────────────────────────────────────────────

def save_escalation(session_id: str, user_name: str, user_email: str, issue: str):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO escalations (session_id,user_name,user_email,issue) "
            "VALUES (?,?,?,?)",
            (session_id, user_name, user_email, issue),
        )


def get_escalations(status: str = None) -> list:
    with _conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM escalations WHERE status=? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM escalations ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def close_escalation(esc_id: int):
    with _conn() as conn:
        conn.execute(
            "UPDATE escalations SET status='closed' WHERE id=?", (esc_id,)
        )
