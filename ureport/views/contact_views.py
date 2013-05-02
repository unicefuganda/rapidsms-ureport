#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
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

from rapidsms.models import Connection, Contact
from poll.models import Poll
from generic.sorters import SimpleSorter
from ureport.forms import ReplyTextForm, DownloadForm, EditReporterForm, SignupForm, ExcelUploadForm, MassTextForm, AssignToNewPollForm, TemplateMessage

from unregister.models import Blacklist
from django.conf import settings
from rapidsms.contrib.locations.models import Location
from django.contrib.auth.models import Group
from ureport.views.utils.excel import handle_excel_file
from ureport.utils import get_contacts, get_contacts2, get_access
from contact.forms import MultipleDistictFilterForm, GenderFilterForm, FilterGroupsForm, AssignGroupForm, RemoveGroupForm
from unregister.forms import BlacklistForm
from ureport.models import Ureporter, UreportContact
from ureport.views.utils.paginator import ureport_paginate
from ureport.forms import UreporterSearchForm, AgeFilterForm


@login_required
def ureporter_profile(request, connection_pk):
    from script.models import ScriptSession, ScriptResponse

    connection = get_object_or_404(Connection, pk=connection_pk)
    session = ScriptSession.objects.filter(connection__pk=connection_pk)

    messages = \
        Message.objects.filter(connection=connection).order_by('-date')
    contact = connection.contact
    if contact:
        #get the proxy
        contact = Ureporter.objects.get(pk=connection.contact.pk)

    reporter_form = EditReporterForm(instance=contact)
    total_outgoing = messages.filter(direction='O',
                                     connection__pk=connection_pk).count()
    total_incoming = messages.filter(direction='I',
                                     connection__pk=connection_pk).count()
    try:
        response_rate = contact.responses.values_list('poll'
        ).distinct().count() * 100 \
                        / float(Poll.objects.filter(contacts=contact).distinct().count())
    except (ZeroDivisionError, ValueError):
        response_rate = None
    gr_poll = Poll.objects.get(pk=121)
    how_did_u_hear = None
    if session:
        try:
            how_did_u_hear = \
                session[0].responses.filter(response__poll=gr_poll)[0].response.message.text
        except (ScriptResponse.DoesNotExist, IndexError):
            how_did_u_hear = 'N/A'
    if request.GET.get('download', None):
        data = []
        data = messages.values_list('text', 'direction', 'date',
                                    'connection__contact__reporting_location__name').iterator()
        headers = ['Message', 'Direction', 'Date', 'District']

        return ExcelResponse(data=data, header=headers)
    columns = [('Message', True, 'text', SimpleSorter()), ('Identifier'
                                                           , True, 'connection', SimpleSorter()), ('Date', True,
                                                                                                   'date',
                                                                                                   SimpleSorter()),
               ('Direction', True, 'direction'
                , SimpleSorter())]

    # hack hack send the reply message by hacking the sendmessage form
    if request.method == 'POST':
        if not request.POST.get('text', None) == u'' \
            and request.POST.get('action') \
                        == u'ureport.forms.ReplyTextForm' and not request.POST.get('page_action', None):
            rep_form = ReplyTextForm(request=request)
            Message.objects.create(
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
                reporter_form=reporter_form,
                objects_per_page=20,
                status_message='Message sent',
                status_message_type='success',
                results_title='Message History',
                selectable=False,
                partial_row='ureport/partials/messages/message_history_row.html',
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
        reporter_form=reporter_form,
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

            (connection, conn_created) = \
                Connection.objects.get_or_create(backend=backend,
                                                 identity=number)
            connection.contact = \
                Contact.objects.create(name=signup_form.cleaned_data['firstname'
                                            ] + ' ' + signup_form.cleaned_data['lastname'])
            contact = connection.contact
            contact.reporting_location = \
                signup_form.cleaned_data['district']

            contact.gender = \
                signup_form.cleaned_data['gender']
            if signup_form.cleaned_data['village']:
                connection.contact.village = \
                    find_closest_match(signup_form.cleaned_data['village'],
                                       Location.objects.filter(type="village"))
            if signup_form.cleaned_data['age']:
                contact.birthdate = datetime.datetime.now() \
                                    - datetime.timedelta(days=365
                                                              * int(signup_form.cleaned_data['age']))

            if signup_form.cleaned_data['group']:
                group_to_match = signup_form.cleaned_data['group']

                if Group.objects.filter(name='Other uReporters').count():
                    default_group = \
                        Group.objects.get(name='Other uReporters')
                    contact.groups.add(default_group)
                if group_to_match:
                    for g in re.findall(r'\w+', group_to_match):
                        if g:
                            group = find_closest_match(str(g),
                                                       Group.objects)
                            if group:
                                connection.contact.groups.add(group)
                                break
            contact.save()
            connection.save()
            status_message = 'You have successfully signed up :)'
            if conn_created:
                Message.objects.create(connection=connection, direction='O'
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


@login_required
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
                export_data['district'] = \
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


@login_required
def bulk_upload_contacts(request):
    """
    bulk upload contacts from an excel file
    """

    if request.method == 'POST':
        contactsform = ExcelUploadForm(request.POST, request.FILES)
        if contactsform.is_valid():
            if contactsform.is_valid() \
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
def blacklist(request, pk):
    contact = Contact.objects.get(pk=int(pk))
    if request.user and request.user.has_perm('unregister.add_blacklist'):
        Blacklist.objects.get_or_create(connection=contact.default_connection)
        Message.objects.create(status="Q", direction="O", connection=contact.default_connection,
                               text="Your UReport opt out is confirmed.If you made a mistake,or you want your voice to be heard again,text in JOIN and send it to 8500!All SMS messages are free")
        return HttpResponse(status=200)


@login_required
def delete(request, pk):
    try:
        contact = Contact.objects.get(pk=int(pk))
        contact.connection_set.clear()
    except Contact.DoesNotExist:
        pass
    return HttpResponseRedirect("/reporter")


@login_required
def ureporters(request):
    access = get_access(request)
    download_form = DownloadForm(request.POST or None)
    if request.POST and request.POST.get('download', None):
        if download_form.is_valid():
            download_form.export(request, request.session['queryset'], 'autoreg_join_date')
        else:
            return HttpResponse("Some thing went wrong")

    columns = [
        ('Identifier', True, 'connection_pk', SimpleSorter()),
        ('Age', True, 'age', SimpleSorter(),),
        ('Gender', True, 'gender', SimpleSorter(),),
        ('Language', True, 'language', SimpleSorter(),),
        ('District', True, 'district', SimpleSorter(),),
        ('Group(s)', True, 'group', SimpleSorter(),),
        ('Questions ', True, 'questions', SimpleSorter(),),
        ('Responses ', True, 'responses', SimpleSorter(),),
        ('Messages Sent', True, 'incoming', SimpleSorter(),),
        ('caregiver', True, 'is_caregiver', SimpleSorter(),),
        ('join date', True, 'autoreg_join_date', SimpleSorter(),),
        ('quit date', True, 'quit_date', SimpleSorter(),),
    ]

    queryset = get_contacts2(request=request)
    if access is not None:
        groups = ",".join(list(access.groups.values_list('name', flat=True)))
        queryset = queryset.filter(group__icontains=groups)
    return generic(request,
                   model=UreportContact,
                   queryset=queryset,
                   download_form=download_form,
                   results_title='uReporters',
                   filter_forms=[UreporterSearchForm, GenderFilterForm, AgeFilterForm, MultipleDistictFilterForm,
                                 FilterGroupsForm],
                   action_forms=[MassTextForm, AssignGroupForm, BlacklistForm, AssignToNewPollForm, RemoveGroupForm,
                                 TemplateMessage],
                   objects_per_page=25,
                   partial_row='ureport/partials/contacts/contacts_row.html',
                   base_template='ureport/ureporters_base.html',
                   paginator_template='ureport/partials/new_pagination.html',
                   paginator_func=ureport_paginate,
                   columns=columns,

    )

