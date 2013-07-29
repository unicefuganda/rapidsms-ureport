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
        csv_rows = csv.reader(open(path, 'rU'), delimiter=",")
        a = open('/home/kenneth/phones.csv', 'wb')
        spam = csv.writer(a, delimiter=",", quotechar="'", quoting=csv.QUOTE_MINIMAL)
        spam.writerow(['identity', 'Phone', 'District'])
        for row in csv_rows:
            con = Connection.objects.get(pk=row[0])
            print "passed"
            spam.writerow([con.pk, con.identity, con.contact.reporting_location])
        a.close()


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

    passE = "Heipoo0afu"
    passS = "mai6aeQuuj"

