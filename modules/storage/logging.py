from modules.provider.prompts import PromptModel
from modules.storage.database import Database
from datetime import datetime
import json
import uuid
import os

class Logging:
    """Persistence for completed email requests."""

    def __init__(self):
        self.db = Database.get()
        # directory to persist JSON log files
        self._json_dir = os.path.join(os.path.dirname(__file__), "db")
        os.makedirs(self._json_dir, exist_ok=True)

    def save_completed_request(self, session, error):
        """Save a completed request to the logs table.

        `session` is the SessionRecord returned by `SessionStore.get_session()`.
        """

        req_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        user_id = getattr(session, "telegram_user_id", None)
        user_message = getattr(session, "user_message", "") or ""
        request_info = getattr(session, "raw_input_json", None) or {}
        state = getattr(session, "state", None)

        # attempt to persist
        try:
            self.db.execute(
                "INSERT INTO logs (request_id, created_at, user_id, user_message, request_info_json, state, error) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    req_id,
                    now,
                    user_id,
                    user_message,
                    json.dumps(request_info),
                    state,
                    error,
                ),
            )

            # also persist request as JSON file
            try:
                log_path = os.path.join(self._json_dir, f"log_{req_id}.json")
                payload = {
                    "request_id": req_id,
                    "created_at": now,
                    "user_id": user_id,
                    "user_message": user_message,
                    "request_info": request_info,
                    "state": state,
                    "error": error,
                }
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
            except Exception:
                # don't let file write errors mask DB errors
                pass

        except Exception:
            raise

