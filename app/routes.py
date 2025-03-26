from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Oleja'}
    courses = [
        {'name': 'Пожарная безопасность 2025',
         'type': 'Безопасность'}, 
        {'name': 'Дискретная математика 2025',
         'type': 'Учебные'}, 
        {'name': 'Функциональное прогаммирование 2025',
         'type': 'Учебные'}, 
    ]
    return render_template('index.html', user=user, courses=courses)
