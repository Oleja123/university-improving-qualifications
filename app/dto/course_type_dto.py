from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseTypeDTO:
    id: Optional[int] = None
    name: Optional[str] = None

    @staticmethod
    def from_form(form, id=None):
        if id is not None:
            return CourseTypeDTO(id=id, name=form.name.data)
        return CourseTypeDTO(name=form.name.data)
