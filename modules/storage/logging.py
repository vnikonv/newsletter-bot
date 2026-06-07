from pydantic import BaseModel
from typing import Optional
from modules.provider.prompts import PromptModel
from modules.storage.database import Database
from datetime import datetime
import json
import uuid

class EmailRequest(BaseModel):
    request_id: str
    created_at: str
    user_id: int
    user_message: str
    request_info: PromptModel
    status: str
    error: Optional[str] = None


class Logging:
    """Persistence for completed email requests."""

    def __init__(self):
        self.db = Database.get()

    def save_completed_request(self, session):
        """Save a completed request to the logs table.

        `session` may be the SessionRecord returned by `SessionStore.get_session()`.
        """

        req_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        user_id = getattr(session, "telegram_user_id", None)
        user_message = getattr(session, "user_message", "") or ""
        request_info = getattr(session, "raw_input_json", None) or {}

        # attempt to persist
        try:
            self.db.execute(
                "INSERT INTO logs (request_id, created_at, user_id, user_message, request_info_json, status, error) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    req_id,
                    now,
                    user_id,
                    user_message,
                    json.dumps(request_info),
                    "COMPLETED",
                    None,
                ),
            )

        except Exception:
            raise

