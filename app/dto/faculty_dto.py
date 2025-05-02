from dataclasses import dataclass
from typing import Optional


@dataclass
class FacultyDTO:
    id: Optional[int] = None
    name: Optional[str] = None