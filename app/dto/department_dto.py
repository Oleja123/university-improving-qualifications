from dataclasses import dataclass
from typing import Optional


@dataclass
class DepartmentDTO:
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    name: Optional[str] = None

    @staticmethod
    def from_form(form, id=None):
        if id is not None:
            return DepartmentDTO(id=id, name=form.name.data, faculty_id=form.faculty.data)
        return DepartmentDTO(name=form.name.data, faculty_id=form.faculty.data)