import csv
from datetime import datetime
from optparse import make_option
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from uganda_common.utils import assign_backend
from rapidsms.models import Connection, Contact
from rapidsms.contrib.locations.models import Location


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="path"),
    )

    def handle(self, **options):
        path = options["path"]
        group = Group.objects.get(name="CODES Bukango")
        district = Location.objects.get(name='Bukomansimbi', type__name='district')
        print "Groups ===============>", group.name
        csv_rows = csv.reader(open(path, 'rU'), delimiter=",")
        rnum = 0
        for row in csv_rows:
            print row
            rnum += 1
            try:
                name, number, gender, age, village, dist, g = tuple(row)
                num = number.replace('-', '').strip()
                name = name.strip().replace("\"", '').replace('\'', "").replace("  ", " ")
            except:
                print 'Row Error:', row
                continue

            num = self.clean_number(num)
            if num:
                number, backend = assign_backend(num)

                connection, created = Connection.objects.get_or_create(identity=number, backend=backend)

                if not created:
                    contact = connection.contact
                    contact.name = name
                    if not contact:
                        contact = Contact.objects.create(name=name)
                else:
                    contact = Contact.objects.create(name=name)

                print "Contact ===>", contact.name
                contact.save()
                if group:
                    contact.groups.add(group)
                contact.village_name = village
                contact.reporting_location = district
                print "Village: District===>", village, district
                if gender.lower().startswith('m'):
                    gender = 'm'
                else:
                    gender = 'f'
                contact.gender = gender
                print "Gender===>", gender
                contact.birthdate = self.birth_date(int(age))
                print "Birth date====>", contact.birthdate

                connection.contact = contact
                connection.save()
                contact.save()
            else:
                print 'Number Error:', row
        print rnum, "================>", group.name

    def clean_number(self, num):
        num = num.strip().replace('+', '').replace('-', '').replace(" ", '')
        if num.startswith('0'):
            num = '256' + num[1:]
        if num.startswith('7') or num.startswith('4') or num.startswith('3'):
            num = '256' + num
        if len(num) == 12 and num.startswith('256'):
            return num
        return None

    def birth_date(self, years):
        return datetime.now() - relativedelta(years=years)

