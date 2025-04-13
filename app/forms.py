from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.models import Faculty
import sqlalchemy as sa
from app import db

class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')


class EditFacultyForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Создать')


class CourseTypeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Создать')


class EditDepartmentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    faculty = SelectField('Факультет', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(EditDepartmentForm, self).__init__(*args, **kwargs)
        faculties = db.session.scalars(sa.select(Faculty)).all()
        self.faculty.choices = [(f.id, f.name) for f in faculties]
