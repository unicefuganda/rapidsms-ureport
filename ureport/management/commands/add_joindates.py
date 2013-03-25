from django.contrib.gis.db import models
from django.core.management import BaseCommand
from rapidsms.models import Connection


class Command(BaseCommand):
    def handle(self,**options):
        for con in Connection.objects.exclude(contact=None)[:25]:
            try:
                created_on = con.messages.order_by('date')[0].date
            except models.ObjectDoesNotExist:
                continue

            con.created_on = created_on
            con.save()
            print con.identity, "Joined on", con.created_on
            print con.identity, "Last modified_on", con.modified_on
            print "=============================================>>>"
            con.contact.created_on = created_on
            con.contact.save()
            print con.contact.name, "Joined on", con.contact.created_on
            print con.contact.name, "Last modified on", con.contact.modified_on
            print "======================================================>>>>>"