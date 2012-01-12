#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand


from poll.models import Poll

from optparse import make_option
from rapidsms_httprouter.models import Message, Connection
from contact.models import MassText
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sites.models import Site
from rapidsms.models import Contact

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-c', '--c', dest='c'),
        make_option('-t', '--t', dest='t'),
         make_option('-u', '--u', dest='u'),
        )

    def handle(self, **options):
        connections = options['p']
        text = options['t']
        user=User.objects.get(pk=int(options['u']))
        conns = Connection.objects.filter(pk__in=eval(options['c'][1:-1])).distinct()

        try:
            messages = Message.mass_text(text, conns)
            MassText.bulk.bulk_insert(send_pre_save=False,
                    user=user,
                    text=text,
                    contacts=Contact.objects.filter(reporting_location__pk__in=conns).values_list('pk',flat=True))
            masstexts = MassText.bulk.bulk_insert_commit(send_post_save=False, autoclobber=True)
            masstext = masstexts[0]
            if settings.SITE_ID:
                masstext.sites.add(Site.objects.get_current())
        except:
            pass





