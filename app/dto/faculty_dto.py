from dataclasses import dataclass
from typing import Optional


@dataclass
class FacultyDTO:
    id: Optional[int] = None
    name: Optional[str] = None

    @staticmethod
    def from_form(form, id=None):
        if id is not None:
            return FacultyDTO(id=id, name=form.name.data)
        return FacultyDTO(name=form.name.data)