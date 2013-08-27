from unittest import TestCase
from rapidsms_ureport.ureport.spreadsheet import Spreadsheet, Row, Cell
from rapidsms_ureport.ureport.management.commands.import_csv_locations import insert_all_locations_into_db, insert_location_types
from rapidsms.contrib.locations.nested.models import Location


class ImportCsvTestCase(TestCase):
    def test_spreadsheet_maps_to_locations(self):
        sheet = Spreadsheet()
        sheet.add_title_row(['COUNTY'])
        row = Row()
        row.append(Cell('Baz'))
        sheet.add_row(row)
        insert_location_types(sheet, 0)
        insert_all_locations_into_db(sheet, 0, 'UTOPIA')

        self.assertEquals('Baz', Location.objects.get(name='Baz').name)
