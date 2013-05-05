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
from script.models import ScriptProgress
from django.db import connection
from optparse import OptionParser, make_option
import urllib2
import urllib
import time
import re
from django.test.client import Client


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option("-d", "--dry_run", dest="dry_run"),
            make_option("-f", "--file", dest="file"),
            make_option("-c", "--code", dest="code"),
            make_option("-p", "--password", dest="password")
        )

    def handle(self, **options):

        dry_run = options['dry_run']
        log_file = options['file']
        code = options['code']
        password = options['password']

        if not log_file:
            log_file = raw_input('Access log to be processed:')
        if not log_file:
#            log_file = "/Users/asseym/ureport_joins.txt"
            log_file = "/Users/asseym/test_assey.txt"
        if not code:
            code = '6262'

        file_handle=open(log_file)
        lines=file_handle.readlines()
        client = Client()
        for line in lines:
            time.sleep(2)
            parts = line.strip().rsplit('] [')
            if not 'Sent' in parts[0]:
                backend_str = parts[0].strip().rsplit('[')[1][5:]
                identity_str = parts[5].strip().rsplit(':')[1]
                if identity_str.startswith('+'):
                    identity_str = identity_str[1:]
                msg_str = parts[8].strip().rsplit(':')[2]
                if dry_run:
                    print backend_str, identity_str, msg_str, '--- to be processed'
                else:
#                    params = urllib.urlencode({'password':'p73xvyqi','backend': backend_str,'sender': identity_str,'message': msg_str})
#                    res = urllib.urlopen('http://localhost:8000/router/receive/?', params)
#                    res = urllib.urlopen('http://test.ureport.unicefuganda.org/router/receive/?', params)
                    params = {'password':password, 'backend': backend_str,'sender': identity_str,'message': msg_str}
                    res = client.get('http://locahhost/router/receive/', params)
                    if ScriptProgress.objects.filter(connection__identity=identity_str, connection__backend__name=backend_str, script__slug__in=['ureport_autoreg2', 'ureport_autoreg_luo2']):
                        print 'Added %s to autoreg...' % identity_str
                    else:
                        print '%s not added to autoreg...' % identity_str



