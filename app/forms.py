from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from app.models import Faculty
import sqlalchemy as sa
from app.services import course_type_service, faculty_service

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
    course_type = SelectField('Тип', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(EditCourseForm, self).__init__(*args, **kwargs)
        course_types = course_type_service.get_all()
        self.course_type.choices = [(t.id, t.name) for t in course_types]

    def from_model(self, model):
        self.name.data = model.name
        self.course_type.data = model.course_type_id


class EditUserForm(FlaskForm):
    full_name = StringField('Полное имя', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired(),
                                                           Length(min=6, message='Имя пользователя должно содержать минимум 6 символов')])
    password = StringField('Пароль', validators=[Optional(), Length(min=6, message='Пароль должен содержать минимум 6 символов')])

    def from_model(self, model):
        self.full_name.data = model.full_name
        self.username.data = model.username

    submit = SubmitField('Создать')