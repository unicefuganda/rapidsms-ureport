import csv
from optparse import make_option
from django.core.management import BaseCommand
from rapidsms.models import Connection


class Command(BaseCommand):
    help = """loads all the districts from a csv, tab-delimited with "name type parent type [lat lon]"
    """
    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="path"),
    )

    def handle(self, **options):
        path = options["path"]
        csv_rows = csv.reader(open(path, 'rU'), delimiter=",")
        for row in csv_rows:
            try:
                connection = Connection.objects.get(identity=row[0])
                contact = connection.contact
                contact.village_name = row[1]
                contact.save()

            except Connection.DoesNotExist:

                print "Number", row[0], "not Found"
