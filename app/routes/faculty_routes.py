from flask import flash, jsonify, redirect, render_template, url_for
from app import app
from flask_login import login_required

from app.dto.faculty_dto import FacultyDTO
from app.forms import EditFacultyForm
from app.services import faculty_service


@app.route('/faculties')
@login_required
def faculties():
    return render_template('faculties/faculties.html', title='Факультеты', faculties=faculty_service.get_all())


@app.route('/faculties/create', methods=['GET', 'POST'])
@login_required
def create_faculty():
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            faculty_service.create(FacultyDTO.from_form(form))
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)

    return render_template('faculties/edit_faculty.html', form=form)


@app.route('/faculties/edit/<faculty_id>', methods=['GET', 'POST'])
@login_required
def edit_faculty(faculty_id):
    form = EditFacultyForm()
    if form.validate_on_submit():
        try:
            faculty_service.update(FacultyDTO.from_form(form, faculty_id))
            return redirect(url_for('faculties'))
        except Exception as ex:
            flash(ex)

    form.from_model(faculty_service.get_by_id(faculty_id))
    return render_template('faculties/edit_faculty.html', form=form)


@app.route('/faculties/delete/<faculty_id>', methods=['DELETE'])
@login_required
def delete_faculty(faculty_id):
    try:
        faculty_service.delete(faculty_id)
        return jsonify({'success': True })
    except Exception as ex:
        flash(ex)