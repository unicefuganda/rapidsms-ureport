#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from ureport.utils import get_flagged_messages
from uganda_common.utils import ExcelResponse
from rapidsms_httprouter.views import receive
from rapidsms_httprouter.models import Message
from django.contrib.auth.decorators import login_required
from generic.views import generic
from ureport.utils import retrieve_poll
from generic.sorters import SimpleSorter
from rapidsms.models import Connection
from contact.models import Flag, MessageFlag

from ureport.forms import SendMessageForm,SearchMessagesForm
from ureport.models import MessageAttribute, MessageDetail
from contact.forms import FlaggedMessageForm
from ureport.views.utils.tags import _get_responses
from contact.forms import FreeSearchTextForm, DistictFilterMessageForm
from generic.sorters import  TupleSorter
from contact.utils import  get_mass_messages, get_messages
from ureport.utils import get_quit_messages,get_autoreg_messages,get_quit_messages,get_unsolicitized_messages,get_poll_messages
from contact.models import MassText
from ureport.models import Ureporter
from ureport.forms import BlacklistForm2,ReplyTextForm
from ureport.views.utils.paginator import ureport_paginate
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from uganda_common.utils import  assign_backend


@login_required
def messages(request):

    filter_forms = [SearchMessagesForm, DistictFilterMessageForm]
    action_forms = [ReplyTextForm, BlacklistForm2]
    partial_row = 'ureport/partials/messages/message_row.html'
    base_template = 'ureport/contact_message_base.html'
    paginator_template = 'ureport/partials/new_pagination.html'
    columns = [('Text', True, 'text', SimpleSorter()),
               ('Contact Information', True, 'connection__contact__name'
               , SimpleSorter()), ('Date', True, 'date',
               SimpleSorter()), ('Type', True, 'application',
               SimpleSorter()), ('Response', False, 'response', None)]
    return generic(
        request,
        model=Message,
        queryset=get_messages,
        filter_forms=filter_forms,
        action_forms=action_forms,
        objects_per_page=25,
        results_title="Message Log",
        partial_row=partial_row,
        base_template=base_template,
        paginator_template=paginator_template,
        paginator_func=ureport_paginate,
        columns=columns,
        sort_column='date',
        sort_ascending=False,
        )

@login_required
def autoreg_messages(request):

    filter_forms = [FreeSearchTextForm, DistictFilterMessageForm]
    action_forms = [ReplyTextForm, BlacklistForm2]
    partial_row = 'ureport/partials/messages/message_row.html'
    base_template = 'ureport/contact_message_base.html'
    paginator_template = 'ureport/partials/new_pagination.html'
    columns = [('Text', True, 'text', SimpleSorter()),
               ('Contact Information', True, 'connection__contact__name'
                , SimpleSorter()), ('Date', True, 'date',
                                    SimpleSorter()), ('Type', True, 'application',
                                                      SimpleSorter()), ('Response', False, 'response', None)]
    return generic(
        request,
        model=Message,
        queryset=get_autoreg_messages,
        filter_forms=filter_forms,
        action_forms=action_forms,
        objects_per_page=25,
        partial_row=partial_row,
        results_title="Autoreg Messages",
        base_template=base_template,
        paginator_template=paginator_template,
        paginator_func=ureport_paginate,
        columns=columns,
        sort_column='date',
        sort_ascending=False,
    )


@login_required
def unsolicitized_messages(request):

    filter_forms = [FreeSearchTextForm, DistictFilterMessageForm]
    action_forms = [ReplyTextForm, BlacklistForm2]
    partial_row = 'ureport/partials/messages/message_row.html'
    base_template = 'ureport/contact_message_base.html'
    paginator_template = 'ureport/partials/new_pagination.html'
    columns = [('Text', True, 'text', SimpleSorter()),
               ('Contact Information', True, 'connection__contact__name'
                , SimpleSorter()), ('Date', True, 'date',
                                    SimpleSorter()), ('Type', True, 'application',
                                                      SimpleSorter()), ('Response', False, 'response', None)]
    return generic(
        request,
        model=Message,
        queryset=get_unsolicitized_messages,
        filter_forms=filter_forms,
        action_forms=action_forms,
        objects_per_page=25,
        partial_row=partial_row,
        base_template=base_template,
        results_title="Unsolicitized Messages",
        paginator_template=paginator_template,
        paginator_func=ureport_paginate,
        columns=columns,
        sort_column='date',
        sort_ascending=False,
    )


@login_required
def poll_messages(request):

    filter_forms = [FreeSearchTextForm, DistictFilterMessageForm]
    action_forms = [ReplyTextForm, BlacklistForm2]
    partial_row = 'ureport/partials/messages/message_row.html'
    base_template = 'ureport/contact_message_base.html'
    paginator_template = 'ureport/partials/new_pagination.html'
    columns = [('Text', True, 'text', SimpleSorter()),
               ('Contact Information', True, 'connection__contact__name'
                , SimpleSorter()), ('Date', True, 'date',
                                    SimpleSorter()), ('Type', True, 'application',
                                                      SimpleSorter()), ('Response', False, 'response', None)]
    return generic(
        request,
        model=Message,
        queryset=get_poll_messages,
        filter_forms=filter_forms,
        action_forms=action_forms,
        objects_per_page=25,
        partial_row=partial_row,
        base_template=base_template,
        results_title="Poll Messages",
        paginator_template=paginator_template,
        paginator_func=ureport_paginate,
        columns=columns,
        sort_column='date',
        sort_ascending=False,
    )


@transaction.autocommit
@login_required
def quit_messages(request):
    filter_forms = [FreeSearchTextForm, DistictFilterMessageForm]
    action_forms = [ReplyTextForm, BlacklistForm2]
    partial_row = 'ureport/partials/messages/message_row.html'
    base_template = 'ureport/contact_message_base.html'
    paginator_template = 'ureport/partials/new_pagination.html'
    columns = [('Text', True, 'text', SimpleSorter()),
               ('Contact Information', True, 'connection__contact__name'
                , SimpleSorter()), ('Date', True, 'date',
                                    SimpleSorter()), ('Type', True, 'application',
                                                      SimpleSorter()), ('Response', False, 'response', None)]
    return generic(
        request,
        model=Message,
        queryset=get_quit_messages,
        filter_forms=filter_forms,
        action_forms=action_forms,
        objects_per_page=25,
        partial_row=partial_row,
        base_template=base_template,
        results_title="Quit Messages",
        paginator_template=paginator_template,
        paginator_func=ureport_paginate,
        columns=columns,
        sort_column='date',
        sort_ascending=False,
    )


@transaction.autocommit
@login_required
def mass_messages(request):
    columns = [('Message', True, 'text', TupleSorter(0)), ('Time',
               True, 'date', TupleSorter(1)), ('User', True, 'user',
               TupleSorter(2)), ('Recipients', True, 'response',
               TupleSorter(3)), ('Type', True, 'type', TupleSorter(4))]

    return generic(
        request,
        model=MassText,
        queryset=get_mass_messages,
        objects_per_page=10,
        partial_row='contact/partials/mass_message_row.html',
        paginator_template='ureport/partials/new_pagination.html',
        paginator_func=ureport_paginate,
        base_template='ureport/contacts_base.html',
        sort_column='date',
        results_title="Mass Messages",
        sort_ascending=False,
        selectable=False,
        )






@login_required
def send_message(request, template='ureport/partials/forward.html'):
    if not request.method == 'POST':
        send_message_form = SendMessageForm()

        if request.GET.get('forward', None):
            msg = request.GET.get('msg')

            template = 'ureport/partials/forward.html'
            message = Message.objects.get(pk=int(msg))
            send_message_form = \
                SendMessageForm(data={'text': message.text,
                                'recipients': ''})
            request.session['mesg'] = message
        if request.GET.get('reply', None):
            msg = request.GET.get('msg')
            message = Message.objects.get(pk=int(msg))
            send_message_form = \
                SendMessageForm(data={'text': message.text,
                                'recipients': message.connection.identity})
            template = 'ureport/partials/reply.html'
            request.session['mesg'] = message
    else:
        send_message_form = SendMessageForm(request.POST)
        if request.GET.get('forward'):
            status = 'forwarded'
        else:
            status = 'replied'
        if send_message_form.is_valid():
            recs = send_message_form.cleaned_data.get('recipients'
                    ).split(',')
            (st, _) = \
                MessageAttribute.objects.get_or_create(name=status)
            (det, _) = \
                MessageDetail.objects.get_or_create(message=request.session['mesg'
                    ], attribute=st, value=send_message_form.cleaned_data.get('text'
                ), description='replied')
            for r in recs:
                try:
                    connection = Connection.objects.get(identity=r)
                except Connection.DoesNotExist:
                    number, backend= assign_backend(r)
                    connection= Connection.objects.create(identity=r,backend=backend)


                #                rate,_=MessageAttribute.objects.get_or_create(name="forwarded")
                #                det,_=MessageDetail.objects.get_or_create(message=message,attribute=rate,value="1",description="forwarded")

                message = Message.objects.create(direction='O',
                        text=send_message_form.cleaned_data.get('text'
                        ), status='Q', connection=connection)

            return HttpResponse('Message Sent :)')
        else:
            return HttpResponse('smothing went wrong')

    return render_to_response(template,
                              {'send_message_form': send_message_form},
                              context_instance=RequestContext(request))


@login_required
@transaction.autocommit
def flagged_messages(request):
    all_flags = Flag.objects.all()
    if request.GET.get('export', None):
        flaggedmessages = MessageFlag.objects.exclude(flag=None)
        data=flaggedmessages.values_list('message__text','message__connection__identity','flag__name','message__date','message__connection__contact__name','message__connection__contact__reporting_location__name')
        data.insert(0,['Message','Mobile Number','Flag','Date','Name','District'])
        return ExcelResponse(data=data)
    return generic(
        request,
        model=MessageFlag,
        queryset=get_flagged_messages,
        objects_per_page=10,
        results_title='Flagged Messages',
        selectable=False,
        partial_row='ureport/partials/messages/flagged_message_row.html'
            ,
        base_template='ureport/flagged_message_base.html',
        columns=[('Message', True, 'message__text', SimpleSorter()),
                 ('Sender Information', True,
                 'message__connection__contact__name', SimpleSorter()),
                 ('Date', True, 'message__date', SimpleSorter()),
                 ('Flags', False, 'message__flagged', None)],
        sort_column='date',
        sort_ascending=False,
        all_flags=all_flags,
        )


@login_required
@transaction.autocommit
def view_flagged_with(request, pk):
    flag = get_object_or_404(Flag, pk=pk)
    messages = flag.get_messages()
    if request.GET.get('export', None):
        export_data=messages.values_list('text','connection__identity','connection__contact__name','connection__contact__reporting_location__name')
        return ExcelResponse(data=export_data)
    return generic(
        request,
        model=Message,
        queryset=messages,
        objects_per_page=25,
        partial_row='contact/partials/message_row.html',
        base_template='ureport/view_flagged_with_base.html',
        results_title='Messages Flagged With %s' % flag.name,
        columns=[('Message', True, 'text', SimpleSorter()),
                 ('Sender Information', True,
                 'connection__contact__name', SimpleSorter()), ('Date',
                 True, 'date', SimpleSorter()), ('Type', True,
                 'application', SimpleSorter())],
        sort_column='date',
        sort_ascending=False,
        )


@login_required
def create_flags(request, pk=None):
    all_flags = Flag.objects.all()
    flag = Flag()
    if pk:
        try:
            flag = Flag.objects.get(pk=int(pk))
        except Flag.DoesNotExist:
            flag = Flag()

    if request.method == 'POST':
        flags_form = FlaggedMessageForm(request.POST, instance=flag)
        if flags_form.is_valid():
            flags_form.save()
            return HttpResponseRedirect('/flaggedmessages')
    else:
        flags_form = FlaggedMessageForm(instance=flag)

    return render_to_response('ureport/new_flag.html',
                              dict(flags_form=flags_form,
                              all_flags=all_flags),
                              context_instance=RequestContext(request))


@login_required
def delete_flag(request, flag_pk):
    flag = get_object_or_404(Flag, pk=flag_pk)
    if flag:
        flag.delete()
        return HttpResponse('Success')
    else:
        return HttpResponse('Failed')

@login_required
def message_feed(request, pks):
    polls = retrieve_poll(request, pks)
    poll = polls[0]
    return render_to_response('/ureport/partials/viz/message_feed.html'
                              , {'poll': poll,
                              'responses': _get_responses(poll)},
                              context_instance=RequestContext(request))


def clickatell_wrapper(request):
    request.GET = request.GET.copy()
    request.GET.update({'backend': 'clickatell',
                       'sender': request.GET['from'],
                       'message': request.GET['text']})
    return receive(request)


