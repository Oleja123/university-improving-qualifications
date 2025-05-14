from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from app import app
from app.decorators.role_decorator import required_role
from app.forms import DateFormFaculty
from app.models import user
from app.services.reports.create_pdf import PdfCreator
from app.services.reports.faculty_report import FacultyReport


@app.route('/reports/faculty', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def faculty_report():
    form = DateFormFaculty()
    if form.validate_on_submit():
        try:
            report = FacultyReport(form.faculty_id.data, form.date_from.data, form.date_to.data)
            return render_template('reports/faculty_report.html', report=report, form=form)
        except Exception as e:
            app.logger.error(e)
            flash('Ошибка при создании отчета')
            return redirect(url_for('faculty_report'))
    return render_template('reports/faculty_report.html', form=form)
        

@app.route('/reports/faculty/download', methods=['GET', 'POST'])
@login_required
@required_role(role=user.ADMIN)
def download_report():
    try:
        date_from = request.args.get()
        report = FacultyReport(form.faculty_id.data, form.date_from.data, form.date_to.data)
        report = PdfCreator(report, )
        return render_template('reports/faculty_report.html', report=report, form=form)
    except Exception as e:
        app.logger.error(e)
        flash('Ошибка при создании отчета')
        return redirect(url_for('faculty_report'))

        
