from dataclasses import dataclass
from typing import Optional


@dataclass
class DepartmentDTO:
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    name: Optional[str] = None