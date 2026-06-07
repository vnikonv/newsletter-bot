from typing import Optional, Dict, Any

from modules.storage.session_store import SessionStore


class StateManager:

    def __init__(self):
        self.store = SessionStore()

    def start_session(self, telegram_user_id: int) -> None:
        self.store.create_session(telegram_user_id)

    def get_session(self, telegram_user_id: int) -> Optional[Any]:
        return self.store.get_session(telegram_user_id)

    def set_state(self, telegram_user_id: int, state: str) -> None:
        self.store.update_session(telegram_user_id, state=state)

    def set_raw_input(self, telegram_user_id: int, raw_input_json: Dict[str, Any]) -> None:
        self.store.update_session(telegram_user_id, raw_input_json=raw_input_json)

    def set_generated_email(self, telegram_user_id: int, generated_email: str) -> None:
        self.store.update_session(telegram_user_id, generated_email=generated_email)

    def delete_session(self, telegram_user_id: int) -> None:
        self.store.delete_session(telegram_user_id)
