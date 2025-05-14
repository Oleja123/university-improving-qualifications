import io
from flask import flash, redirect, render_template, request, send_file, url_for
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
            if form.generate.data:
                return render_template('reports/faculty_report.html', report=report, form=form)
            if form.download.data:
                pdf = PdfCreator()
                pdf.create_table(report, [45, 45, 45, 45])
                pdf_output = pdf.output(dest='S')
                return send_file(
                    io.BytesIO(pdf_output),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='report.pdf'
                )
        except Exception as e:
            app.logger.error(e)
            flash('Ошибка при работе с отчетом')
            return redirect(url_for('faculty_report'))
    return render_template('reports/faculty_report.html', form=form)
        