from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class Stand:
    name: str
    status: str
    occupied_by: str | None = None
    occupied_since: datetime | None = None

    def take(self, user_name: str, when: datetime) -> "Stand":
        return replace(self, status="occupied", occupied_by=user_name, occupied_since=when)

    def release(self) -> "Stand":
        return replace(self, status="free", occupied_by=None, occupied_since=None)
