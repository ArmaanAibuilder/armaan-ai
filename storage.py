import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "armaan_ai.db"


def connect():
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def init_db():
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_messages_chat
                ON messages(conversation_id, id);
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
        """)


def create_conversation(title="New Chat"):
    now = timestamp()
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
            (title, now, now),
        )
        return cursor.lastrowid


def list_conversations():
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_messages(conversation_id):
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def add_message(conversation_id, role, content):
    if role not in ("user", "assistant"):
        raise ValueError("Role must be user or assistant.")
    now = timestamp()
    with connect() as db:
        db.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, now),
        )
        db.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id),
        )


def delete_conversation(conversation_id):
    with connect() as db:
        db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))


def list_memories():
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM memories ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def add_memory(content):
    content = " ".join(str(content).split()).strip()
    if not content:
        return
    with connect() as db:
        db.execute(
            "INSERT OR IGNORE INTO memories (content, created_at) VALUES (?, ?)",
            (content, timestamp()),
        )


def delete_memory(memory_id):
    with connect() as db:
        db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))


def rename_conversation(conversation_id, new_title):
    new_title = " ".join(str(new_title).split()).strip()
    if not new_title:
        raise ValueError("Chat title cannot be empty.")
    with connect() as db:
        db.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (new_title[:80], timestamp(), conversation_id),
        )


init_db()
