from datetime import date
from flask import current_app
from fpdf import FPDF

class PdfCreator(FPDF):

    def __init__(self):
        super().__init__()
        self.line_height = self.font_size + 2
        self.add_font('DejaVu', '', 'app/static/fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'app/static/fonts/DejaVuSans-Bold.ttf', uni=True)

    def _to_str(self, text):
        if not text:
            return 'Отсутствует'
        elif isinstance(text, date):
            return text.isoformat()
        else:
            return str(text)

    def draw_row(self, row, col_widths):
        cell_heights = []
        for i, text in enumerate(row):
            text = self._to_str(text)
            nb_lines = self.multi_cell(
                col_widths[i],
                self.line_height,
                text,
                border=0,
                split_only=True,
            )
            cell_heights.append(self.line_height * len(nb_lines))

        max_height = max(cell_heights)

        if self.get_y() + max_height > self.page_break_trigger:
            self.add_page()

        x_start = self.get_x()
        y_start = self.get_y()

        for i, text in enumerate(row):
            text = self._to_str(text)
            x = self.get_x()
            self.rect(x, y_start, col_widths[i], max_height)
            self.multi_cell(
                col_widths[i],
                self.line_height,
                text,
                border=0,
                align='L'
            )
            self.set_xy(x + col_widths[i], y_start)

        self.set_y(y_start + max_height)


    def add_row(self, row, col_widths):

        col_lines = []
        for col_data, col_width in zip(row, col_widths):
            col_data = str(col_data)
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