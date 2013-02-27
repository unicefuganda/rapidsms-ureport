import csv
from optparse import make_option
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from uganda_common.utils import assign_backend
from rapidsms.models import Connection, Contact

__author__ = 'kenneth'


class Command(BaseCommand):
    help = """loads all the districts from a csv, tab-delimited with "name type parent type [lat lon]"
    """
    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="path"),
    )

    def handle(self, **options):
        path = options["path"]
        group = Group.objects.get(name="UNITED NATIONS ALL STAFF")
        csv_rows = csv.reader(open(path, 'rU'), delimiter=",")
        rnum = 0
        for row in csv_rows:

            try:
                org, title, name, designation, mobile = tuple(row)
                mobiles = mobile.replace('-', '').strip().split('/')
                name = name.strip().replace("\"", '').replace('\'', "").replace("  ", " ")
            except:
                print 'Row Error:', row
                continue

            for num in mobiles:
                num = self.clean_number(num)
                if num:
                    number, backend = assign_backend(num)

                    connection, created = Connection.objects.get_or_create(identity=number, backend=backend)

                    if not created:
                        contact = connection.contact
                        if not contact:
                            contact = Contact.objects.create(name=name)
                    else:
                        contact = Contact.objects.create(name=name)

                    if group:
                        contact.groups.add(group)

                    contact.occupation = "%s/%s" % (org.strip().replace("\"", '').replace('\'', "").replace("  ", " "),
                                                    designation.strip().replace("\"", '').replace('\'', "").replace(
                                                        "  ", " "))

                    connection.contact = contact
                    connection.save()
                else:
                    print 'Number Error:', row

    def clean_number(self, num):
        num = num.strip().replace('+', '').replace('-', '').replace(" ", '')
        if num.startswith('0'):
            num = '256' + num[1:]
        if num.startswith('7') or num.startswith('4') or num.startswith('3'):
            num = '256' + num
        if len(num) == 12 and num.startswith('256'):
            return num
        return None

