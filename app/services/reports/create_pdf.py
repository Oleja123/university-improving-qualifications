from datetime import date

from fpdf import FPDF

from app.services.reports.pdf_draw_row import PdfDrawRow


class ReportCreator(PdfDrawRow):

    def __init__(self):
        super().__init__()

    def _to_str(self, text):
        if not text:
            return 'Отсутствует'
        elif isinstance(text, date):
            return text.isoformat()
        else:
            return str(text)

    def create_table(self, report, col_widths, report_name):
        self.add_page()
        self.set_font("DejaVu", size=16)
        self.set_font(style="B")

        self.multi_cell(
            text=f"{report_name}: {report.filter_item_name}", w=120, border=0, align='C')
        self.ln()

        self.set_font("DejaVu", size=10)
        self.set_font(style="B")
        self.multi_cell(text=report.date_from, w=120, border=0, align='C')
        self.ln()
        self.multi_cell(text=report.date_to, w=120, border=0, align='C')
        self.ln()
        self.draw_row(report.table_header, col_widths)

        self.set_font(style="")
        for row in report.rows:
            self.draw_row(row, col_widths)
        self.set_font(style="B")
        lst = ['' for i in range(len(col_widths))]
        lst[0] = 'Итоговое количество пройденных курсов'
        lst[-1] = report.result
        self.draw_row(lst, col_widths)
        lst[0] = report.percent_target
        lst[-1] = report.percent
        self.draw_row(lst, col_widths)
