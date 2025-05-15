from fpdf import FPDF
from app import app

class PdfCreator(FPDF):

    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', 'app/static/fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'app/static/fonts/DejaVuSans-Bold.ttf', uni=True)

    def add_row(self, row, col_widths):

        col_lines = []

        for col_data, col_width in zip(row, col_widths):
            lines = (self.get_string_width(str(col_data)) + 2) // col_width + 1
            col_lines.append(lines)

        row_height = max(col_lines) * self.font_size

        if self.y + row_height > self.page_break_trigger:
            self.add_page()

        for col_data, col_width in zip(row, col_widths):
            self.multi_cell(
                col_width,
                row_height,
                str(col_data),
                border=1,
                new_x="RIGHT",
                new_y="TOP"
            )
        for i in range(int(max(col_lines))):
            self.ln()

    def create_table(self, report, col_widths, report_name):
        self.add_page()
        self.set_font("DejaVu", size=16)
        self.set_font(style="B")

        self.multi_cell(text=f"{report_name}: {report.filter_item_name}", w=120, border=0, align='C')
        self.ln()

        self.set_font("DejaVu", size=10)
        self.set_font(style="B")
        self.add_row(report.table_header, col_widths)

        self.set_font(style="")
        for row in report.rows:
            self.add_row(row, col_widths)
        self.set_font(style="B")
        lst = ['' for i in range(len(col_widths))]
        lst[0] = 'Итоговое количество пройденных курсов'
        lst[-1] = report.result
        self.add_row(lst, col_widths)
