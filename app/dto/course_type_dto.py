from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseTypeDTO:
    id: Optional[int] = None
    name: Optional[str] = None
