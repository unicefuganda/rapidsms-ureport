#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.shortcuts import  get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from uganda_common.utils import ExcelResponse
from rapidsms_httprouter.models import Message
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict
from generic.views import generic
from django.core.files import File
from uganda_common.utils import assign_backend
from script.utils.handling import find_closest_match
import re
import datetime


@login_required
def ureporter_profile(request, connection_pk):
    from script.models import ScriptSession, ScriptResponse

    connection = get_object_or_404(Connection, pk=connection_pk)
    session = ScriptSession.objects.filter(connection__pk=connection_pk)

    messages =\
    Message.objects.filter(connection=connection).order_by('-date')

    contact = connection.contact
    total_outgoing = messages.filter(direction='O',
        connection__pk=connection_pk).count()
    total_incoming = messages.filter(direction='I',
        connection__pk=connection_pk).count()
    try:
        response_rate = contact.responses.values_list('poll'
        ).distinct().count() * 100\
        / float(Poll.objects.filter(contacts=contact).distinct().count())
    except (ZeroDivisionError, ValueError):
        response_rate = None
    gr_poll = Poll.objects.get(pk=121)
    how_did_u_hear = None
    if session.exists():
        try:
            how_did_u_hear =\
            session[0].responses.filter(response__poll=gr_poll)[0].response.message.text
        except (ScriptResponse.DoesNotExist, IndexError):
            how_did_u_hear = 'N/A'
    if request.GET.get('download',None):

        data = []
        for message in messages:
            rep = {}

            rep['Message'] = message.text
            rep['direction']=message.direction
            rep['date']=message.date.date()
            rep['Mobile Number'] = message.connection.identity


            if message.connection.contact:
                rep['name'] = message.connection.contact.name
                rep['district'] = message.connection.contact.reporting_location
            else:
                rep['name'] = ''
                rep['district'] = ''
            data.append(rep)

        return ExcelResponse(data=data)
    columns = [('Message', True, 'text', SimpleSorter()), ('connection'
                                                           , True, 'connection', SimpleSorter()), ('Date', True,
                                                                                                   'date',
                                                                                                   SimpleSorter()),
        ('Direction', True, 'direction'
         , SimpleSorter())]

    # hack hack send the reply message by hacking the sendmessage form
    if request.method == 'POST':
        if not request.POST.get('text', None) == u''\
        and request.POST.get('action')\
        == u'ureport.forms.ReplyTextForm':
            Message.objects.create(date=datetime.datetime.now(),
                connection=connection, direction='O'
                , status='Q',
                text=request.POST.get('text'))
            return generic(
                request,
                model=Message,
                queryset=messages,
                total_outgoing=total_outgoing,
                total_incoming=total_incoming,
                response_rate=response_rate,
                how_did_u_hear=how_did_u_hear,
                contact=contact,
                objects_per_page=20,
                status_message='Message sent',
                status_message_type='success',
                results_title='Message History',
                selectable=False,
                partial_row='ureport/partials/messages/message_history_row.html'
                ,
                base_template='ureport/message_history_base.html',
                action_forms=[ReplyTextForm],
                columns=columns,
                sort_column='date',
                sort_ascending=False,
            )

    return generic(
        request,
        model=Message,
        queryset=messages,
        contact=contact,
        total_outgoing=total_outgoing,
        total_incoming=total_incoming,
        response_rate=response_rate,
        objects_per_page=20,
        how_did_u_hear=how_did_u_hear,
        results_title='Message History',
        selectable=False,
        partial_row='ureport/partials/messages/message_history_row.html'
        ,
        base_template='ureport/message_history_base.html',
        action_forms=[ReplyTextForm],
        columns=columns,
        sort_column='date',
        sort_ascending=False,
    )

@login_required
def deleteReporter(request, reporter_pk):
    reporter = get_object_or_404(Contact, pk=reporter_pk)
    if request.method == 'POST':
        reporter.delete()
    return HttpResponse(status=200)


@login_required
def editReporter(request, reporter_pk):
    reporter = get_object_or_404(Contact, pk=reporter_pk)
    reporter_form = EditReporterForm(instance=reporter)
    if request.method == 'POST':
        reporter_form = EditReporterForm(instance=reporter,
            data=request.POST)
        if reporter_form.is_valid():
            reporter_form.save()
        else:
            return render_to_response('ureport/partials/contacts/edit_reporter.html'
                , {'reporter_form': reporter_form, 'reporter'
                : reporter},
                context_instance=RequestContext(request))
        return render_to_response('/ureport/partials/contacts/contacts_row.html'
            , {'object'
               : Contact.objects.get(pk=reporter_pk),
               'selectable': True},
            context_instance=RequestContext(request))
    else:
        return render_to_response('ureport/partials/contacts/edit_reporter.html'
            , {'reporter_form': reporter_form,
               'reporter': reporter},
            context_instance=RequestContext(request))

def signup(request):
    status_message = None
    if request.method == 'POST':
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            mobile = signup_form.cleaned_data['mobile']
            (number, backend) = assign_backend(mobile)

            # create our connection

            (connection, created) =\
            Connection.objects.get_or_create(backend=backend,
                identity=number)
            connection.contact =\
            Contact.objects.create(name=signup_form.cleaned_data['firstname'
                                        ] + ' ' + signup_form.cleaned_data['lastname'])
            connection.contact.reporting_location =\
            signup_form.cleaned_data['district']
            connection.contact.gender =\
            signup_form.cleaned_data['gender']
            connection.contact.village =\
            find_closest_match(signup_form.cleaned_data['village'],
                Location.objects)
            connection.contact.birthdate = datetime.datetime.now()\
            - datetime.timedelta(days=365
            * int(signup_form.cleaned_data['age']))

            group_to_match = signup_form.cleaned_data['group']

            if Group.objects.filter(name='Other uReporters').count():
                default_group =\
                Group.objects.get(name='Other uReporters')
                connection.contact.groups.add(default_group)
            if group_to_match:
                for g in re.findall(r'\w+', group_to_match):
                    if g:
                        group = find_closest_match(str(g),
                            Group.objects)
                        if group:
                            connection.contact.groups.add(group)
                            break

            connection.save()
            status_message = 'You have successfully signed up :)'
            Message.objects.create(date=datetime.datetime.now(),
                connection=connection, direction='O'
                , status='Q',
                text='CONGRATULATIONS!!! You are now a registered member of Ureport! With Ureport, you can make a real difference!  Speak Up and Be Heard! from UNICEF'
            )
        else:
            return render_to_response('ureport/signup.html',
                dict(signup_form=signup_form),
                context_instance=RequestContext(request))
    signup_form = SignupForm()
    return render_to_response('ureport/signup.html',
        dict(signup_form=signup_form,
            status_message=status_message),
        context_instance=RequestContext(request))




def get_all_contacts(request):
    from uganda_common.utils import ExcelResponse

    contacts = Contact.objects.all()
    export_data_list = []
    for contact in contacts:
        if contact.name:
            export_data = SortedDict()
            export_data['name'] = contact.name
            if contact.gender:
                export_data['sex'] = contact.gender
            else:
                export_data['sex'] = 'N/A'
            if contact.birthdate:
                try:
                    contact.birthdate.tzinfo = None
                    export_data['age'] = (datetime.datetime.now()
                                          - contact.birthdate).days / 365
                except:
                    continue
            else:
                export_data['age'] = 'N/A'
            if contact.reporting_location:
                export_data['district'] =\
                contact.reporting_location.name
            else:
                export_data['district'] = 'N/A'
            if contact.village:
                export_data['village'] = contact.village.name
            else:
                export_data['village'] = 'N/A'
            if contact.groups.count() > 0:
                export_data['group'] = contact.groups.all()[0].name
            else:
                export_data['group'] = 'N/A'

            export_data_list.append(export_data)

    response = ExcelResponse(export_data_list)
    return response

def bulk_upload_contacts(request):
    """
    bulk upload contacts from an excel file
    """

    if request.method == 'POST':
        contactsform = ExcelUploadForm(request.POST, request.FILES)
        if contactsform.is_valid():
            if contactsform.is_valid()\
            and request.FILES.get('excel_file', None):
                fields = [
                    'telephone number',
                    'name',
                    'district',
                    'county',
                    'village',
                    'age',
                    'gender',
                    ]
                message = handle_excel_file(request.FILES['excel_file'
                ], contactsform.cleaned_data['assign_to_group'
                ], fields)
            return render_to_response('ureport/bulk_contact_upload.html'
                , {'contactsform': contactsform, 'message'
                : message},
                context_instance=RequestContext(request))

    contactsform = ExcelUploadForm()
    return render_to_response('ureport/bulk_contact_upload.html',
            {'contactsform': contactsform},
        context_instance=RequestContext(request))





def download_contacts_template(request, f):
    path = getattr(settings, 'DOWNLOADS_FOLDER', None)
    fh = open(path + f)
    data = File(fh).read()
    response = HttpResponse(data, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=' + f
    return response


@login_required
def blacklist(request,pk):
    contact=Contact.objects.get(pk=int(pk))
    if request.user and request.user.has_perm('unregister.add_blacklist'):
        Blacklist.objects.get_or_create(connection=contact.default_connection)
        Message.objects.create(status="Q",direction="O",connection=contact.default_connection,text="Your UReport opt out is confirmed.If you made a mistake,or you want your voice to be heard again,text in JOIN and send it to 8500!All SMS messages are free")
        return HttpResponse(status=200)