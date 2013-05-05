from django.core.management.base import BaseCommand
import traceback
import os
from script.models import ScriptSession
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact, Connection
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
from unregister.models import Blacklist
from django.conf import settings
from rapidsms_httprouter.models import Message
from django.db import connection
from optparse import OptionParser, make_option
import urllib2
import re


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option("-d", "--dry_run", dest="dry_run"),
            make_option("-f", "--file", dest="file"),
            make_option("-p", "--poll", dest="poll"),
        )
    
    def handle(self, **options):
        
        dry_run = options['dry_run']
        log_file = options['file']
        poll_pk = options['poll']
        
        if not poll_pk:
            poll_pk = raw_input('Poll ID:')
            
        if not log_file:
            log_file = raw_input('Access log to be processed:')
        if not log_file:
            log_file = "/Users/asseym/Public/rapidsms/ureport/ureport_project/rapidsms_ureport/ureport/ureport_prod.access.log.1"
        
        try:
            poll = Poll.objects.get(pk=poll_pk)
        except Poll.DoesNotExist:
            pass
        file_handle=open(log_file)
        lines=file_handle.readlines()
        for line in lines:
            parts = line.strip().rsplit(' ')
            http_status = parts[6]
            query_string = parts[4]
            query_parts = query_string.split('=')
            try:
                count = 0
                backend_name = query_parts[2][:-7]
                connection = query_parts[3]
                message = urllib2.unquote(query_parts[4]).replace('+', ' ')
                if connection.endswith('&message'):
                    if not http_status in ['200', '400']:
                        if backend_name in ['Agregator1', 'zain']:
                            identity = connection[3:15] if connection.startswith('%') else connection[:12]
                            if not identity == 'Warid&messag':
                                try:
                                    conn=Connection.objects.get(identity=identity, backend__name=backend_name)
                                    msg=Message.objects.filter(connection=conn, text=message, direction="I")
                                    if msg.exists():
                                        print msg, ' --- exists!'
                                    else:
                                        if not dry_run:
                                            msg=Message.objects.create(connection=conn, text=message, direction="I")
                                            print "created: "+msg.text
                                            try:
                                                if poll.contacts.filter(pk=conn.contact.pk):
                                                    poll.process_response(msg)
                                            except AttributeError:
                                                pass
                                        else:
                                            print message, ' --- to be created'
                                except Connection.DoesNotExist:
                                    print identity, ' --- connection does not exists'
            except IndexError:
                pass



