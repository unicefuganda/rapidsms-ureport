#!/usr/bin/python
# -*- coding: utf-8 -*-

from rapidsms_httprouter.models import Message
from django.contrib.auth.decorators import login_required
from generic.views import generic
from rapidsms.models import Contact, Connection
from generic.sorters import SimpleSorter
from django.db import transaction


@login_required
def ussd_manager(request):
    ussd_contacts = Contact.objects.filter(groups__name='equatel')
    ussd_conns = Connection.objects.filter(contact__in=ussd_contacts)
    messages = \
        Message.objects.filter(connection__in=ussd_conns).order_by('-date'
            )

    return generic(
        request,
        model=Message,
        queryset=messages,
        objects_per_page=25,
        partial_row='contact/partials/message_row.html',
        base_template='ureport/ussd_messages_base.html',
        results_title='Ussd Messages',
        columns=[('Message', True, 'text', SimpleSorter()),
                 ('Date', True, 'date', SimpleSorter()),
                 ('Type', True, 'application', SimpleSorter())],
        sort_column='date',
        sort_ascending=False,
        )
