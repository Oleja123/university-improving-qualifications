import io
from flask import current_app, flash, redirect, render_template, send_file, url_for
from flask_login import login_required
from app.decorators.role_decorator import required_role
from app.main.forms import ReportForm
from app.models import user
from app.services import course_type_service, faculty_service
from app.services.reports.course_type_report import CourseTypeReport
from app.services.reports.create_report import ReportCreator
from app.services.reports.departments_report import DepartmentsReport
from app.services.reports.faculty_report import FacultyReport
from app.main import bp


@bp.route('/reports/faculty', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def faculty_report():
    form = ReportForm(filter=faculty_service.get_all(),
                      filter_name='Факультет')
    if form.validate_on_submit():
        try:
            report = FacultyReport(form.filter_id.data,
                                   form.date_from.data, form.date_to.data)
            if form.generate.data:
                return render_template('reports/report.html', report=report, form=form,
                                       page_title='Отчеты по факультетам',
                                       title='Отчет по факультету',
                                       report_title='Отчет по факультету')
            if form.download.data:
                pdf = ReportCreator()
                pdf.create_table(
                    report, [36, 36, 36, 36, 36], 'Отчет по факультету')
                pdf_output = pdf.output(dest='S')
                return send_file(
                    io.BytesIO(pdf_output),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='report.pdf'
                )
        except Exception as e:
            current_app.logger.error(e)
            flash('Ошибка при работе с отчетом')
            return redirect(url_for('main.faculty_report'))
    return render_template('reports/report.html', form=form,
                           page_title='Отчеты по факультетам',
                           title='Отчет по факультету',
                           report_title='Отчет по факультету')


@bp.route('/reports/course_type', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def course_type_report():
    form = ReportForm(filter=course_type_service.get_all(),
                      filter_name='Тип курсов')
    if form.validate_on_submit():
        try:
            report = CourseTypeReport(
                form.filter_id.data, form.date_from.data, form.date_to.data)
            if form.generate.data:
                return render_template('reports/report.html', report=report, form=form,
                                       page_title='Отчеты по типам курсов',
                                       title='Отчет по типу курсов',
                                       report_title='Отчет по типу курсов')
            if form.download.data:
                pdf = ReportCreator()
                pdf.create_table(
                    report, [36, 36, 36, 36, 36], 'Отчет по типу курсов')
                pdf_output = pdf.output(dest='S')
                return send_file(
                    io.BytesIO(pdf_output),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='report.pdf'
                )
        except Exception as e:
            current_app.logger.error(e)
            flash('Ошибка при работе с отчетом')
            return redirect(url_for('main.course_type_report'))
    return render_template('reports/report.html', form=form,
                           page_title='Отчеты по типам курсов',
                           title='Отчет по типу курсов',
                           report_title='Отчет по типу курсов')


@bp.route('/reports/departments', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def departments_report():
    form = ReportForm(filter=faculty_service.get_all(),
                      filter_name='Факультет')
    if form.validate_on_submit():
        try:
            report = DepartmentsReport(
                form.filter_id.data, form.date_from.data, form.date_to.data)
            if form.generate.data:
                return render_template('reports/report.html', report=report, form=form,
                                       page_title='Отчеты по кафедрам',
                                       title='Отчет по кафедрам факультета',
                                       report_title='Отчет по кафедрам факультета')
            if form.download.data:
                pdf = ReportCreator()
                pdf.create_table(
                    report, [60, 60, 60], 'Отчет по кафедрам факультета')
                pdf_output = pdf.output(dest='S')
                return send_file(
                    io.BytesIO(pdf_output),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='report.pdf'
                )
        except Exception as e:
            current_app.logger.error(e)
            flash('Ошибка при работе с отчетом')
            return redirect(url_for('main.departments_report'))
    return render_template('reports/report.html', form=form,
                           page_title='Отчеты по кафедрам',
                           title='Отчет по кафедрам факультета',
                           report_title='Отчет по кафедрам факультета')
