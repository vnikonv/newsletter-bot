from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
from dataclasses import dataclass

from modules.storage.database import Database


class Session(BaseModel):
    telegram_user_id: int
    state: str
    user_message: str
    email_text: Optional[str] = None
    recipient_email: Optional[str] = None
    created_at: str
    updated_at: str


@dataclass
class SessionRecord:
    telegram_user_id: int
    state: str
    user_message: Optional[str]
    email_text: Optional[str]
    recipient_email: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    raw_input_json: Optional[dict] = None
    generated_email: Optional[str] = None


class SessionStore:

    def __init__(self):
        self.db = Database.get()

    def create_session(self, telegram_user_id: int):
        now = datetime.utcnow().isoformat()
        self.db.execute(
            "INSERT OR REPLACE INTO sessions (telegram_user_id, state, user_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_user_id, "STARTED", "", now, now),
        )

    def update_session(self, telegram_user_id: int, **kwargs):
        # allowed columns
        cols = []
        params = []
        for k, v in kwargs.items():
            if k == "raw_input_json":
                cols.append("raw_input_json = ?")
                params.append(json.dumps(v))
            elif k == "generated_email":
                cols.append("generated_email = ?")
                params.append(v)
            elif k in ("state", "user_message", "email_text", "recipient_email"):
                cols.append(f"{k} = ?")
                params.append(v)

        if not cols:
            return

        params.append(telegram_user_id)
        sql = f"UPDATE sessions SET {', '.join(cols)}, updated_at = ? WHERE telegram_user_id = ?"
        # we want updated_at before the WHERE param
        updated_at = datetime.utcnow().isoformat()
        # insert updated_at before telegram_user_id
        params.insert(len(params) - 1, updated_at)
        self.db.execute(sql, tuple(params))

    def get_session(self, telegram_user_id: int) -> Optional[SessionRecord]:
        row = self.db.query_one("SELECT * FROM sessions WHERE telegram_user_id = ?", (telegram_user_id,))
        if not row:
            return None

        try:
            raw = json.loads(row["raw_input_json"]) if row["raw_input_json"] else None
        except Exception:
            raw = None

        return SessionRecord(
            telegram_user_id=row["telegram_user_id"],
            state=row["state"],
            user_message=row["user_message"],
            email_text=row["email_text"],
            recipient_email=row["recipient_email"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            raw_input_json=raw,
            generated_email=row["generated_email"],
        )

    def delete_session(self, telegram_user_id: int):
        self.db.execute("DELETE FROM sessions WHERE telegram_user_id = ?", (telegram_user_id,))
