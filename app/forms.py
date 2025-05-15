from flask_wtf import FlaskForm
from wtforms import DateField, FileField, StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
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

class UploadForm(FlaskForm):
    file = FileField('Выберите файл', validators=[DataRequired()])
    submit = SubmitField('Загрузить')

class TeachersCoursesForm(FlaskForm):
    course_name = StringField('Название курса', validators=[Optional()])
    user_full_name = StringField('Имя преподавателя', validators=[Optional()])
    course_type_id = SelectField('Тип курсов')
    is_approved = SelectField('Приняты')

    def __init__(self, *args, **kwargs):
        super(TeachersCoursesForm, self).__init__(*args, **kwargs)
        course_types = course_type_service.get_all()
        self.course_type_id.choices = [(t.id, t.name) for t in course_types]
        self.course_type_id.choices.insert(0, ('', ''))
        self.is_approved.choices = []
        self.is_approved.choices.append(('', ''))
        self.is_approved.choices.append(('true', 'Принятые'))
        self.is_approved.choices.append(('false', 'Непринятые'))


class ReportForm(FlaskForm):
    date_from = DateField('Начальная дата отчета')
    date_to = DateField('Конечная дата отчета')
    filter_id = SelectField(validators=[DataRequired()], coerce=int)
    generate = SubmitField('Сформировать отчет')
    download = SubmitField('Скачать отчет')

    def __init__(self, filter=None, filter_name=None, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.filter_id.choices = [(f.id, f.name) for f in filter]
        if filter_name:
            self.filter_id.label.data = filter_name
