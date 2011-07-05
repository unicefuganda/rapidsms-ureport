import datetime

from django.core.management.base import BaseCommand
from script.models import *

from rapidsms.models import Backend, Connection, Contact
from rapidsms_httprouter.models import Message
from django.utils.encoding import smart_unicode, smart_str

class Command(BaseCommand):

    help = """dumps all ureporters and their message histories
    """

    def handle(self, **options):
        print smart_str("ID\tname\tgender\tage\tgroups\tdistrict ID\tdistrict name\tvillage ID\tvillage name\tMESSAGE HISTORY")
        for c in Contact.objects.all():
            name = smart_unicode(c.name.replace("\n","").replace("\r","")) if c.name else u''
            gender = c.gender or ''
            age = str(int((datetime.datetime.now() - c.birthdate).days / 365.0)) if c.birthdate else ''
            groups = ','.join(c.groups.values_list('name',flat=True))
            msgs = []
            for m in Message.objects.filter(connection__contact=c).order_by('date').values_list('text',flat=True):
                msgs.append(smart_str(m.replace("\n","").replace("\r","")))
            message_history = smart_str("\t").join(msgs)
            location_pk = str(c.reporting_location.pk) if c.reporting_location else ''
            location_name = c.reporting_location.name if c.reporting_location else ''
            village_pk = str(c.village.pk) if c.village else ''
            village_name = c.village.name if c.village else ''
            try:
                print smart_str(smart_str("%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s") % (c.pk,name,gender,age,groups,location_pk,location_name,village_pk,village_name,message_history))
            except UnicodeDecodeError:
                continue
