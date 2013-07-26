class Column:
    def __init__(self):
        self.cells = []
        self.index = None
        self.name = None

    def append(self, cell):
        self.cells.append(cell)

    def get_unique_cells(self):
        seen = list()
        unique_cells = list()
        for cell in self.cells:
            if cell.value not in seen:
                seen.append(cell.value)
                unique_cells.append(cell)
        return unique_cells


class Row:
    def __init__(self):
        self.cells = []
        self.index = 0

    def append(self, cell):
        self.cells.append(cell)
        cell.x = self.index
        cell.y = len(self.cells) - 1

    def get_left_cell(self, cell):
        if cell.y == 0:
            return None
        else:
            return self.cells[cell.y - 1]

    def get_cell(self, position):
        return self.cells[position]


class Cell:
    def __init__(self, value):
        self.value = value
        self.x = 0
        self.y = 0


class Spreadsheet:

    def __init__(self):
        self.rows = []
        self.current_column = -1
        self.title_row = []

    def add_row(self, row):
        self.rows.append(row)
        row.index = len(self.rows) - 1

    def add_title_row(self, title_row):
        self.title_row = title_row

    def get_next_column(self):
        if self.has_next_column():
            column = self.extract_column(self.current_column + 1)
            self.current_column += 1
            column.index = self.current_column
            column.name = self.title_row[self.current_column]
            return column
        return None

    def extract_column(self, index):
        column = Column()
        for row in self.rows:
            column.append(row.get_cell(index))
        return column

    def has_next_column(self):
        if len(self.rows) == 0:
            return False
        elif self.current_column >= len(self.rows[0].cells) - 1:
            return False
        return True

    def get_left_cell(self, cell):
        parent_row_index = cell.x
        parent_row = self.rows[parent_row_index]
        return parent_row.get_left_cell(cell)

