from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.models import Faculty
import sqlalchemy as sa
from app import db
from app.services import faculty_service

class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')


class EditFacultyForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Создать')
    
    def from_model(self, model):
        self.name.data = model.name


class EditCourseTypeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Создать')

    def from_model(self, model):
        self.name.data = model.name

class EditDepartmentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    faculty = SelectField('Факультет', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(EditDepartmentForm, self).__init__(*args, **kwargs)
        faculties = faculty_service.get_all()
        self.faculty.choices = [(f.id, f.name) for f in faculties]

    def from_model(self, model):
        self.name.data = model.name
        self.faculty.data = model.faculty_id


class EditCourseForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    type = SelectField('Тип', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(EditCourseForm, self).__init__(*args, **kwargs)
        types = TypeService.get_all
        self.type.choices = [(t.id, t.name) for t in types]