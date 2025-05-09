from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDTO:
    id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_fired: Optional[bool] = None
    role: Optional[int] = None

    @staticmethod
    def from_form(form, role=None, id=None):
        if id is not None:
            return UserDTO(id=id, full_name=form.full_name.data, username=form.username.data, password=form.password.data, role=role)
        return UserDTO(full_name=form.full_name.data, username=form.username.data, password=form.password.data, role=role)