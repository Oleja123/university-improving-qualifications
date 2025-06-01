from datetime import date
from flask import current_app
from fpdf import FPDF

class PdfDrawRow(FPDF):

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

