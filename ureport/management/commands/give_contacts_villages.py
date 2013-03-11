from optparse import make_option
from django.core.management import BaseCommand
from rapidsms.models import Contact, Connection
import xlrd

__author__ = 'kenneth'


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="file"),
    )


    def handle(self, *args, **options):
        excel = options['file']
        if not excel: raise RuntimeError("Insert Excel File: Where is the excel file to process")
        contacts = self.read_all_facilities(excel)
        for contact in contacts:
            try:
                c = Connection.objects.get(identity=str(contact[1]).replace(".", "").replace("e+11", ""))
                con = c.contact
                con.village_name = contact[2]
                con.save()
                print "Gave %s to %s" % (con.name, con.village_name)
            except Connection.DoesNotExist:
                print str(contact[1]).replace(".", "").replace("e+11", ""), "Does not exist"


    def read_all_facilities(self, excel):
        wb = xlrd.open_workbook(excel)
        l = []
        num_of_sheets = 1
        for i in xrange(num_of_sheets):
            sh = wb.sheet_by_index(i)
            for rownum in range(sh.nrows):
                vals = sh.row_values(rownum)
                l.append(vals)
        return l
