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
from contact.models import Flag,MessageFlag


from ureport.forms import SendMessageForm
from ureport.models import MessageAttribute,MessageDetail
from contact.forms import FlaggedMessageForm
from ureport.views.utils.tags import _get_responses



@login_required
def send_message(request):
    if not request.method =="POST":
        send_message_form=SendMessageForm()

        if request.GET.get('forward',None):
            msg=request.GET.get('msg')

            template="ureport/partials/forward.html"
            message=Message.objects.get(pk=int(msg))
            send_message_form=SendMessageForm(data={'text':message.text,'recipients':''})
            request.session['mesg']=message
        if request.GET.get('reply',None):
            msg=request.GET.get('msg')
            message=Message.objects.get(pk=int(msg))
            send_message_form=SendMessageForm(data={'text':message.text,'recipients':message.connection.identity})
            template="ureport/partials/reply.html"
            request.session['mesg']=message
    else:
        send_message_form=SendMessageForm(request.POST)
        if request.GET.get('forward'):
            status="forwarded"
        else:
            status="replied"
        if send_message_form.is_valid():
            recs=send_message_form.cleaned_data.get('recipients').split(',')
            st,_=MessageAttribute.objects.get_or_create(name=status)
            det,_=MessageDetail.objects.get_or_create(message=request.session['mesg'],attribute=st,value="1",description="replied")
            for r in recs:
                connection=Connection.objects.get(identity=r)
                #                rate,_=MessageAttribute.objects.get_or_create(name="forwarded")
                #                det,_=MessageDetail.objects.get_or_create(message=message,attribute=rate,value="1",description="forwarded")
                message=Message.objects.create(direction="O",text=send_message_form.cleaned_data.get('text'),status="Q",connection=connection)

            return HttpResponse('Message Sent :)')
        else:
            return HttpResponse("smothing went wrong")

    return render_to_response(template,{'send_message_form':send_message_form},context_instance=RequestContext(request))


@login_required
def flagged_messages(request):
    all_flags = Flag.objects.all()
    if request.GET.get('export', None):
        flaggedmessages = MessageFlag.objects.exclude(flag=None)

        data = []
        for mf in flaggedmessages:
            rep = {}

            rep['Message'] = mf.message.text
            rep['Mobile Number'] = mf.message.connection.identity
            rep['flag'] = mf.flag.name
            rep['date']=mf.message.date.date()
            if mf.message.connection.contact:
                rep['name'] = mf.message.connection.contact.name
                rep['district'] = mf.message.connection.contact.reporting_location
            else:
                rep['name'] = ''
                rep['district'] = ''

            data.append(rep)

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
        all_flags=all_flags

    )

@login_required
def view_flagged_with(request, pk):
    flag = get_object_or_404(Flag, pk=pk)
    messages = flag.get_messages()
    if request.GET.get('export', None):
        data = []
        for message in messages:
            rep = {}

            rep['Message'] = message.text
            rep['Mobile Number'] = message.connection.identity
            rep['flag'] = flag.name
            if message.connection.contact:
                rep['name'] = message.connection.contact.name
                rep['district'] = message.connection.contact.reporting_location
            else:
                rep['name'] = ''
                rep['district'] = ''
            data.append(rep)

        return ExcelResponse(data=data)
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
                                                                                            'application',
                                                                                            SimpleSorter())],
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


def message_feed(request, pks):
    polls = retrieve_poll(request, pks)
    poll = polls[0]
    return render_to_response('/ureport/partials/viz/message_feed.html'
        , {'poll': poll, 'responses'
        : _get_responses(poll)},
        context_instance=RequestContext(request))

def clickatell_wrapper(request):
    request.GET = request.GET.copy()
    request.GET.update({'backend': 'clickatell', 'sender'
    : request.GET['from'], 'message'
    : request.GET['text']})
    return receive(request)