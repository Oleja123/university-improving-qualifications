import io

from flask import abort, current_app, flash, jsonify, make_response, redirect, render_template, request, send_file, url_for
from flask_login import login_required, current_user

from app.decorators.role_decorator import required_role
from app.dto.notification_dto import NotificationDTO
from app.dto.user_dto import UserDTO
from app.main.forms import EditUserForm
from app.models import user
from app.services import course_service, notification_service, user_service, department_service
from app.main import bp
from app.services.reports.create_direction import DirectionCreator


@bp.route('/users')
@login_required
@required_role(role=user.ADMIN)
def users():
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', None, type=int)
    is_fired = request.args.get('is_fired', None, type=str)
    if is_fired == '':
        is_fired = None
    if is_fired is not None and is_fired == 'True':
        is_fired = True
    if is_fired is not None and is_fired == 'False':
        is_fired = False
    users = user_service.get_all_paginated(
        page, UserDTO(is_fired=is_fired, role=role))
    return render_template('users/users.html',
                           title='Пользователи',
                           users=users)


@bp.route('/users/<user_id>/qualifications')
@login_required
@required_role(role=user.ADMIN)
def create_user_qualifications(user_id):
    try:
        page = request.args.get('page', 1, type=int)
        teacher = user_service.get_by_id(user_id)
        if teacher.role != user.TEACHER:
            raise ValueError('Создать квалификацию можно только для преподавателя')

        courses = course_service.get_all_paginated(page)
        return render_template('users/create_user_qualification.html',
                            title='Квалификация пользователя',
                            user=teacher,
                            courses=courses)
    except ValueError as e:
        abort(404)
    except Exception as e:
        abort(500)



@bp.route("/users/<user_id>/qualifications/download", methods=["POST"])
@login_required
@required_role(role=user.ADMIN)
def download_user_qualifications(user_id):
    try:
        teacher = user_service.get_by_id(user_id)
        courses = request.form.getlist("selected")
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        place = request.form.get("place")

        if not courses:
            raise ValueError("Не выбраны курсы")

        if not date_from or not date_to:
            raise ValueError("Даты начала и окончания обязательны")

        pdf = DirectionCreator(teacher, courses, date_from, date_to, place, current_user)
        pdf.create_table()
        pdf_output = pdf.output(dest="S")
        current_app.logger.info('ВКИД')
        return send_file(
            io.BytesIO(pdf_output),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="direction.pdf"
        )

    except ValueError as e:
        current_app.logger.warning(f"Validation error: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": str(e)}), 400
        flash(str(e))
        return redirect(request.referrer or '/')

    except Exception as e:
        current_app.logger.exception("Ошибка при создании направления")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Внутренняя ошибка сервера"}), 500
        flash("Ошибка при создании направления")
        return redirect(request.referrer or '/')



@bp.route('/users/create_admin', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def create_admin():
    form = EditUserForm()
    if form.validate_on_submit():
        try:
            user_service.create(UserDTO.from_form(form, 0))
            return redirect(url_for('main.users'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.create_admin'))

    return render_template('users/edit_user.html',
                           title='Создать сотрудника',
                           form=form)


@bp.route('/users/create_teacher', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def create_teacher():
    form = EditUserForm()
    if form.validate_on_submit():
        try:
            user_service.create(UserDTO.from_form(form, 1))
            return redirect(url_for('main.users'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.create_teacher'))

    return render_template('users/edit_user.html',
                           title='Создать преподавателя',
                           form=form)


@bp.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def edit_user(user_id):
    form = EditUserForm()
    if form.validate_on_submit():
        try:
            user_service.update(UserDTO.from_form(form, id=user_id))
            return redirect(url_for('main.users'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.edit_user', user_id=user_id))
    try:
        page = request.args.get('page', 1, type=int)
        search_request = request.args.get('department_name', '', type=int)
        user = user_service.get_by_id(user_id)
        form.from_model(user)
    except ValueError as e:
        flash(e)
        return redirect(request.referrer or url_for('main.faculties'))
    except Exception as e:
        flash('Ошибка при редактировании пользователя')
        return redirect(request.referrer or url_for('main.faculties'))
        

    return render_template('users/edit_user.html', form=form, user=user,
                           user_departments=user_service.get_departments(
                               UserDTO(user_id)),
                           title='Редактировать пользователя',
                           departments=department_service.get_all_paginated(page=page, search_request=search_request))


@bp.route('/users/delete/<user_id>', methods=['DELETE'])
@login_required
@required_role(role=user.ADMIN)
def delete_user(user_id):
    try:
        if current_user.get_id() == user_id:
            return jsonify({"error": 'Нельзя удалить себя'}), 500
        user_service.delete(user_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users/fire/<user_id>', methods=['POST'])
@login_required
@required_role(role=user.ADMIN)
def fire_user(user_id):
    try:
        if current_user.get_id() == user_id:
            return jsonify({"error": 'Нельзя заблокировать себя'}), 500
        user_service.fire(user_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users/<user_id>/remove_from_department/<department_id>', methods=['DELETE'])
@login_required
@required_role(role=user.ADMIN)
def remove_from_department(user_id, department_id):
    try:
        user_service.remove_from_department(user_id, department_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users/<user_id>/add_to_department/<department_id>', methods=['POST'])
@login_required
@required_role(role=user.ADMIN)
def add_to_department(user_id, department_id):
    try:
        user_service.add_to_department(user_id, department_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/users/send_notification/<user_id>', methods=['POST'])
@login_required
@required_role(role=user.ADMIN)
def send_notification(user_id):
    try:
        data = request.get_json()
        msg = data.get('message')
        notification_service.send_message(
            NotificationDTO(user_id=user_id, message=msg))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
