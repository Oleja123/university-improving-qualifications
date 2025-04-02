from app.models import User, Role, Department, Faculty
from app import app, db
import sqlalchemy as sa
import unittest
import os
os.environ['DATABASE_URL'] = 'sqlite://'


class FacultyModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_crud(self):
        f1 = Faculty(name='FIST')
        db.session.add(f1)
        db.session.commit()
        self.assertEqual(f1.name, db.session.scalar(
            sa.select(Faculty).where(Faculty.name == f1.name)).name)
        f2 = Faculty(name='EF')
        db.session.add(f2)
        db.session.commit()
        self.assertEqual(len(db.session.scalars(sa.select(Faculty)).all()), 2)
        db.session.delete(f2)
        db.session.commit()
        self.assertEqual(len(db.session.scalars(sa.select(Faculty)).all()), 1)
        f1.name = 'PIST'
        db.session.commit()
        self.assertEqual(db.session.scalar(sa.select(Faculty)).name, 'PIST')

    def test_departments(self):
        f1 = Faculty(name='FIST')
        db.session.add(f1)
        db.session.commit()
        d1 = Department(name='IS', faculty=f1)
        d2 = Department(name='CT', faculty=f1)
        db.session.add(d1, d2)
        db.session.commit()
        f1.departments.add(d1)
        f1.departments.add(d2)
        db.session.commit()
        self.assertEqual(len(db.session.scalars(
            f1.departments.select()).all()), 2)
        f1.departments.remove(d2)
        self.assertEqual(len(db.session.scalars(
            f1.departments.select()).all()), 1)


class DepartmentModelCase(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_crud(self):
        d1 = Department(name='IS')
        db.session.add(d1)
        db.session.commit()
        self.assertEqual(d1.name, db.session.scalar(
            sa.select(Department).where(Department.name == d1.name)).name)
        d2 = Department(name='CT')
        db.session.add(d2)
        db.session.commit()
        self.assertEqual(
            len(db.session.scalars(sa.select(Department)).all()), 2)
        db.session.delete(d2)
        db.session.commit()
        self.assertEqual(
            len(db.session.scalars(sa.select(Department)).all()), 1)
        d1.name = 'ICC'
        db.session.commit()
        self.assertEqual(db.session.scalar(sa.select(Department)).name, 'ICC')

    def test_teachers(self):
        d1 = Department(name='IS')
        db.session.add(d1)
        db.session.commit()
        t1 = User(username='eegov', email='eegov@ulstu.ru',
                  full_name='Egov Eugene Nikolaeevich')
        t2 = User(username='tr0n1n', email='tr0n1n@ulstu.ru',
                  full_name='Tronin Vadim Georgeovich')
        r = Role(name='Teacher')
        db.session.add(t1, t2)
        db.session.add(r)
        t1.set_role(r.name)
        t2.set_role(r.name)
        db.session.commit()
        d1.add_teacher(t1)
        d1.add_teacher(t2)
        self.assertEqual(
            len(db.session.scalars(d1.teachers.select()).all()), 2)
        d1.teachers.remove(t2)
        self.assertEqual(
            len(db.session.scalars(d1.teachers.select()).all()), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
