import csv
from rapidsms_ureport.ureport.spreadsheet import Spreadsheet, Row, Cell


def read_csv(file_name):
    file = open(file_name, 'rU')
    reader = csv.reader(file)

    rows = []
    for row in reader:
        rows.append(row)
    return rows


def make_spreadsheet(rows):
    sheet = Spreadsheet()
    row_index = -1
    for row in rows:
        row_index += 1
        if row_index == 0:
            sheet.add_title_row(row)
        else:
            sheet_row = Row()
            sheet.add_row(sheet_row)
            for entry in row:
                sheet_row.append(Cell(entry))
    return sheet


def get_locations_file_as_spreadsheet(file_name):
    rows = read_csv(file_name)
    return make_spreadsheet(rows)