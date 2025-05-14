from fpdf import FPDF


class PdfCreator(FPDF):

    def add_row(self, row, col_widths):

        col_lines = []

        for col_data, col_width in zip(row, col_widths):
            lines = (self.get_string_width(col_data) + 2) // col_width + 1
            col_lines.append(lines)

        row_height = max(col_lines) * self.font_size

        for col_data, col_width in zip(row, col_widths):
            self.multi_cell(
            col_width,
            row_height,
            str(col_data),
            border=1,
            new_x="RIGHT",
            new_y="TOP"
            )
        self.ln()

    def create_table(self, report, col_widths):
        self.set_font(style="B")
        self.add_row(report.header, col_widths)
        self.ln()
    
        self.set_font(style="")
        for row in report.rows:
            self.add_row(row, col_widths)
