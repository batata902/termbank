from __future__ import annotations

from socket import socket
from src import User
class Session:
    def __init__(self):

        self.user: User | None = None
        self.username: str = None

    @property
    def is_auth(self) -> bool:
        return self.session is not None

    def load_session(self, session: Session) -> None:
        self.user = session.user
        self.username = session.username
