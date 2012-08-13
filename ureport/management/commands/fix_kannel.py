from django.core.management.base import BaseCommand
import traceback
import os
from script.models import ScriptSession
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
from unregister.models import Blacklist
from django.conf import settings
from rapidsms_httprouter.models import Message
from django.db import connection
from optparse import OptionParser, make_option
import re
from rapidsms.models import Connection
from rapidsms_httprouter.router import get_router

class Command(BaseCommand):


    def handle(self, **options):

        #file1=open("/home/mossplix/log_8.txt")
        file2=open("/home/mossplix/incoming2.log")
        files=[file2]
        num=re.compile('([0-9]+)')
        for f in files:
            lines=f.readlines()
            for line in lines:
                parts=line.strip().rsplit('[FID:]')[1].split('] [')
                identity=num.search(parts[1]).groups()[0]
                message_text=parts[4].split(':')[2]

                try:
                    connection=Connection.objects.get(identity=identity)
                    msg=Message.objects.filter(connection__identity=identity,text__icontains=message_text,direction="I")
                    if msg.exists():
                        pass
                    else:
                        router=get_router()
                        router.handle_incoming(connection.backend.name, connection.identity, message_text)

#                        with open("/home/mossplix/desc.log", "r+") as f:
#                            old = f.read() # read everything in the file
#                            f.seek(0) # rewind
#                            f.write(line + old)

#                        msg=Message.objects.create(connection__identity=identity,text=message_text,direction="I")
#                        print "created "+msg.text
#                        if poll.objects.filter(pk=connection.contact.pk):
#                            poll.process_response(msg)
                except Connection.DoesNotExist:
                    pass



