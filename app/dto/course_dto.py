from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseDTO:
    id: Optional[int] = None
    name: Optional[str] = None
    course_type_id: Optional[int] = None

    @staticmethod
    def from_form(form, id=None):
        if id is not None:
            return CourseDTO(id=id, name=form.name.data, course_type_id=form.course_type.data)
        return CourseDTO(name=form.name.data, course_type_id=form.course_type.data)
