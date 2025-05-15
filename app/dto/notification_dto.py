from dataclasses import dataclass
from typing import Optional


@dataclass
class NotificationDTO:
    id: Optional[int] = None
    user_id: Optional[int] = None
    message: Optional[str] = None
