import os
import sqlite3
import json
from threading import Lock

DB_DIR = os.path.join(os.path.dirname(__file__), "db")
DB_PATH = os.path.join(DB_DIR, "app.db")


class Database:

    _instance = None
    _lock = Lock()

    def __init__(self, path: str = DB_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = Database()
            return cls._instance

    def _ensure_schema(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                telegram_user_id INTEGER PRIMARY KEY,
                state TEXT,
                user_message TEXT,
                recipient_email TEXT,
                raw_input_json TEXT,
                generated_email TEXT,
                final_prompt TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                request_id TEXT PRIMARY KEY,
                created_at TEXT,
                user_id INTEGER,
                user_message TEXT,
                request_info_json TEXT,
                state TEXT,
                error TEXT
            )
            """
        )

        self.conn.commit()

    def execute(self, sql: str, params: tuple = ()):  # pragma: no cover - thin wrapper
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def query_one(self, sql: str, params: tuple = ()):  # pragma: no cover - thin wrapper
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()
