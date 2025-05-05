from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseDTO:
    id: Optional[int] = None
    name: Optional[str] = None
    course_type_id: Optional[int] = None
