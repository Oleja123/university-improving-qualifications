from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin


users_roles = sa.Table(
    'users_roles',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id'),
              primary_key=True)
)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Role(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)

    def __repr__(self):
        return f'Role {self.name}'


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    full_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    roles: so.WriteOnlyMapped['Role'] = so.relationship(secondary=users_roles)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, role: str) -> bool:
        query = self.roles.select().where(Role.name == role)
        return db.session.scalar(query) is not None

    def get_roles(self) -> list[Role]:
        if self.roles is None:
            return None
        try:
            query = self.roles.select()
            return db.session.scalars(query).all()
        except:
            return None

    def remove_roles(self, roles: list[str]) -> bool:
        roles = set(roles)
        roles = list(roles)
        query = sa.select(Role).where(Role.name.in_(roles))
        res = db.session.scalars(query).all()
        if res is None:
            return False
        if type(res) is not list:
            res = [res]
        current_roles = [role.name for role in self.get_roles()]
        for role in res:
            if role.name in current_roles:
                self.roles.remove(role)
        return True

    def add_roles(self, roles: list[str]) -> bool:
        query = sa.select(Role).where(Role.name.in_(roles))
        res = db.session.scalars(query).all()
        if res is None:
            return False
        if res is not list:
            res = [res]
        current_roles = [i.name for i in self.get_roles()]
        for role in res:
            if not role.name in current_roles:
                self.roles.add(role)
        return True

    def __repr__(self):
        return f'User {self.username}'
