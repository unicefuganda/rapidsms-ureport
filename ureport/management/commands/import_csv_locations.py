from django.core.management import BaseCommand
from rapidsms.contrib.locations.nested.models import Location
from rapidsms.contrib.locations.models import LocationType, Point
from rapidsms_ureport.ureport import csv_reader


class Command(BaseCommand):

    def handle(self, *args, **options):
        if len(args) < 1:
            print("You must pass the 0-based index of the column holding the reporting level as an argument")
            exit(-1)
        else:
            reporting_level = int(args[1])
            sheet = csv_reader.get_locations_file_as_spreadsheet(args[0])
            insert_location_types(sheet, reporting_level)
            insert_all_locations_into_db(sheet, reporting_level, root_node_name="country")


def insert_location_types(sheet, reporting_level):
    for i in range(len(sheet.title_row)):
        location_type_name = sheet.title_row[i]
        if i == reporting_level:
            LocationType.objects.create(name=location_type_name, slug='district')
        else:
            LocationType.objects.create(name=location_type_name, slug=location_type_name)


def add_location(loc_name, parent, location_point, type_id=None):
    Location.objects.create(name=loc_name, tree_parent=parent, type_id=type_id, point=location_point, code=loc_name)


def insert_all_locations_into_db(sheet, reporting_level, root_node_name):
    Location.objects.create(name=root_node_name)
    location_point = Point.objects.create(latitude=0, longitude=0)
    while sheet.has_next_column():
        column = sheet.get_next_column()
        cells = column.get_unique_cells()
        type_id = None
        if column.index == reporting_level:
            type_id = 'district'

        if column.index == 0:
            parent = Location.objects.get(name=root_node_name)
            for cell in cells:
                add_location(cell.value, parent, location_point, type_id=type_id)
        else:
            for cell in cells:
                left = sheet.get_left_cell(cell)
                parent = Location.objects.get(name=left.value, level=column.index)
                add_location(cell.value, parent, location_point, type_id=type_id)


