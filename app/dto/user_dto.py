from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDTO:
    id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[int] = None