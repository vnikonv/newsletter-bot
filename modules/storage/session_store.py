from typing import Optional
import json
from datetime import datetime
from dataclasses import dataclass, asdict
import os

from modules.storage.database import Database

@dataclass
class SessionRecord:
    telegram_user_id: int
    state: str
    user_message: Optional[str]
    recipient_email: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    raw_input_json: Optional[dict] = None
    final_prompt: Optional[str] = None
    generated_email: Optional[str] = None


class SessionStore:

    def __init__(self):
        self.db = Database.get()
        # directory to persist JSON session files
        self._json_dir = os.path.join(os.path.dirname(__file__), "db")
        os.makedirs(self._json_dir, exist_ok=True)

    def create_session(self, telegram_user_id: int):
        now = datetime.utcnow().isoformat()
        self.db.execute(
            "INSERT OR REPLACE INTO sessions (telegram_user_id, state, user_message, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (telegram_user_id, "STARTED", "", now, now),
        )
        # persist session as JSON file
        session = self.get_session(telegram_user_id)
        if session:
            try:
                self._write_session_json(session)
            except Exception:
                # don't let file write errors break DB behavior
                pass

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
            elif k == "final_prompt":
                cols.append("final_prompt = ?")
                params.append(v)
            elif k in ("state", "user_message", "recipient_email"):
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
        # persist updated session as JSON file
        session = self.get_session(telegram_user_id)
        if session:
            try:
                self._write_session_json(session)
            except Exception:
                pass

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
            recipient_email=row["recipient_email"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            raw_input_json=raw,
            final_prompt=row["final_prompt"],
            generated_email=row["generated_email"],
        )

    def delete_session(self, telegram_user_id: int):
        self.db.execute("DELETE FROM sessions WHERE telegram_user_id = ?", (telegram_user_id,))
        # remove JSON file if present
        try:
            path = os.path.join(self._json_dir, f"session_{telegram_user_id}.json")
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    def _write_session_json(self, session_record: SessionRecord):
        """Write a session record to the `db/` folder as JSON."""
        try:
            data = asdict(session_record)
            # ensure any nested raw_input_json is JSON-serializable
            path = os.path.join(self._json_dir, f"session_{session_record.telegram_user_id}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception:
            raise
