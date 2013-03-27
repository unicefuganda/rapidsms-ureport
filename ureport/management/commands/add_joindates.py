from django.contrib.gis.db import models
from django.core.management import BaseCommand
from django.db import transaction
from django.db.utils import DatabaseError
from rapidsms.models import Connection


class Command(BaseCommand):
    def handle(self,**options):
        for con in Connection.objects.filter(created_on=None).exclude(contact=None):
            try:
                created_on = con.messages.filter(direction__iexact='o').order_by('date')[0].date
            except IndexError, e:
                print e
                print 'No contacts'
                continue
            except DatabaseError:
                try:
                    transaction.rollback()
                except Exception, e:
                    print 'Big Error'
                    print e
                    pass
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