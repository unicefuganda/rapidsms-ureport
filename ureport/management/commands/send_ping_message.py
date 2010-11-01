from rapidsms_httprouter.router import get_router
from rapidsms.messages.outgoing import OutgoingMessage
from django.core.management.base import BaseCommand
from rapidsms.models import Connection
from django.conf import settings
import datetime

class Command(BaseCommand):
    

    def handle(self, **options):
        try:
            import pdb;pdb.set_trace()
            connection = Connection.objects.get(identity=settings.PING_NUMBER)
            text = datetime.datetime.now().strftime('Worked at %H:%M %Y-%m-%d')
            get_router().handle_outgoing(OutgoingMessage(connection, text))
        except:
            print "exception"
            pass
        