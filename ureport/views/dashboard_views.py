#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from uganda_common.utils import ExcelResponse

from rapidsms_httprouter.models import Message

from ureport.forms import AssignResponseGroupForm, SelectPoll, \
    NewPollForm, rangeForm, DistrictForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from rapidsms.models import Contact, Connection
from unregister.models import Blacklist
from poll.models import Translation, Poll
from ureport.models import MessageAttribute, AlertsExport, Settings, \
    MessageDetail
from django.core.paginator import EmptyPage, PageNotAnInteger
import datetime
from ureport.views.utils.paginator import UreportPaginator
from contact.models import Flag
from django.db.models import Q
from ureport.settings import UREPORT_ROOT
from ureport.utils import get_access
import os


@login_required
def mp_dashboard(request):
    from contact.forms import FilterGroupsForm, \
        MultipleDistictFilterForm, GenderFilterForm, AgeFilterForm

    mp_contacts = Contact.objects.filter(groups__name__in=['MP'])

    forms = [MultipleDistictFilterForm, FilterGroupsForm,
             GenderFilterForm, AgeFilterForm]
    filter_forms = []
    mp_conns = Connection.objects.filter(contact__in=mp_contacts)
    contacts = \
        Contact.objects.exclude(connection__in=Blacklist.objects.all()).distinct()
    message_list = Message.objects.filter(connection__in=mp_conns,
                                          direction='I').order_by('-date')
    if request.GET.get('ajax', None):
        date = datetime.datetime.now() - datetime.timedelta(seconds=15)
        msgs = Message.objects.filter(connection__in=mp_conns,
                                      direction='I').filter(date__gte=date)
        msgs_list = []
        if msgs:
            for msg in msgs:
                m = {}
                m['text'] = msg.text
                m['date'] = str(msg.date.date())
                m['name'] = msg.connection.contact.name
                m['number'] = msg.connection.identity
                if msg.connection.contact.reporting_location:
                    m['district'] = \
                        msg.connection.contact.reporting_location.name
                else:
                    m['district'] = 'N/A'

                m['group'] = msg.connection.contact.groups.all()[0].name
                msgs_list.append(m)
            return HttpResponse(mark_safe(simplejson.dumps(msgs_list)))
        else:
            return HttpResponse('success')

    old_contacts = contacts
    if request.POST and request.GET.get('filter', None):
        for form_class in forms:
            form_instance = form_class(request.POST, request=request)
            if form_instance.is_valid():
                contacts = form_instance.filter(request, contacts)
        if old_contacts.count() == contacts.count():
            return HttpResponse('No Contacts Selected')
        else:
            request.session['filtered'] = contacts
            return HttpResponse(str(contacts.count()))
    for form in forms:
        filter_forms.append(form(**{'request': request}))
    paginator = UreportPaginator(message_list, 10, body=6, padding=2)
    page = request.GET.get('page', 1)
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:

        # If page is not an integer, deliver first page.

        messages = paginator.page(1)
    except EmptyPage:

        # If page is out of range (e.g. 9999), deliver last page of results.

        messages = paginator.page(paginator.num_pages)
    poll_form = NewPollForm()
    poll_form.updateTypes()

    if request.method == 'POST' and request.GET.get('poll', None):
        res_dict = request.POST.copy()
        res_dict.update({'groups': u'2'})
        poll_form = NewPollForm(res_dict)
        poll_form.updateTypes()

        # create poll

        if request.session.get('filtered', None) \
            and poll_form.is_valid():
            name = poll_form.cleaned_data['name']
            p_type = poll_form.cleaned_data['type']
            response_type = poll_form.cleaned_data['response_type']
            question = poll_form.cleaned_data['question']
            default_response = poll_form.cleaned_data['default_response'
            ]

            if not poll_form.cleaned_data['default_response_luo'] == '' \
                and not poll_form.cleaned_data['default_response'] \
                            == '':
                (translation, created) = \
                    Translation.objects.get_or_create(language='ach',
                                                      field=poll_form.cleaned_data['default_response'
                                                      ],
                                                      value=poll_form.cleaned_data['default_response_luo'
                                                      ])

            if not poll_form.cleaned_data['question_luo'] == '':
                (translation, created) = \
                    Translation.objects.get_or_create(language='ach',
                                                      field=poll_form.cleaned_data['question'],
                                                      value=poll_form.cleaned_data['question_luo'])

            poll_type = (Poll.TYPE_TEXT if p_type
                                           == NewPollForm.TYPE_YES_NO else p_type)

            poll = Poll.create_with_bulk(
                name,
                poll_type,
                question,
                default_response,
                request.session.get('filtered'),
                request.user,
            )
            return redirect(reverse('poll.views.view_poll',
                                    args=[poll.pk]))

    context_dict = {
        'poll_form': poll_form,
        'filter_forms': filter_forms,
        'messages': messages,
    }

    return render_to_response('ureport/mp_dashboard.html',
                              context_dict,
                              context_instance=RequestContext(request))


@login_required
def alerts(request):
    access = get_access(request)
    poll_form = NewPollForm()
    range_form = rangeForm()
    poll_form.updateTypes()
    assign_polls = Poll.objects.exclude(start_date=None).order_by('-pk')[0:5]
    district_form = DistrictForm(request.POST or None)
    if request.GET.get('reset_districts', None):
        request.session['districts'] = None
        request.session['groups'] = None

    if district_form.is_valid():
        request.session['districts'] = [c.pk for c in district_form.cleaned_data['districts']]

    groupform = AssignResponseGroupForm(request=request, access=access)
    if request.method == 'POST' and request.POST.get('groups', None):
        g_form = AssignResponseGroupForm(request.POST, request=request)
        if g_form.is_valid():
            request.session['groups'] = g_form.cleaned_data['groups']

    template = 'ureport/polls/alerts.html'
    if request.session.get('districts'):
        message_list = \
            Message.objects.filter(details__attribute__name='alert'

            ).filter(connection__contact__reporting_location__in=request.session.get('districts'))
    else:
        message_list = Message.objects.filter(details__attribute__name='alert')

    if request.session.get('groups', None):
        message_list = message_list.filter(connection__contact__groups__in=request.session.get('groups'
        ))

    if access:
        message_list = message_list.filter(connection__contact__groups__in=access.groups.all())
    (capture_status, _) = \
        Settings.objects.get_or_create(attribute='alerts')
    (rate, _) = MessageAttribute.objects.get_or_create(name='rating')

    # message_list=[Message.objects.latest('date')]
    # use more efficient count

    if request.GET.get('download', None) and access is None:
        range_form = rangeForm(request.POST)
        if range_form.is_valid():
            start = range_form.cleaned_data['startdate']
            end = range_form.cleaned_data['enddate']
            from django.core.servers.basehttp import FileWrapper

            cols = ["replied", "rating", "direction", "district", "date", "message", "id",
                    "forwarded"]
            data = AlertsExport.objects.filter(date__range=(start, end)).values_list(*cols).iterator()
            excel_file_path = \
                os.path.join(os.path.join(os.path.join(UREPORT_ROOT,
                                                       'static'), 'spreadsheets'),
                             'alerts.xlsx')
            ExcelResponse(data, output_name=excel_file_path,
                          write_to_file=True, headers=cols)
            response = HttpResponse(FileWrapper(open(excel_file_path)),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=alerts.xlsx'
            from django import db

            db.reset_queries()
            response['Cache-Control'] = 'no-cache'
            return response

    if request.GET.get('search', None):
        search = request.GET.get('search')
        if search[0] == '"' and search[-1] == '"':
            search = search[1:-1]
            message_list = message_list.filter(Q(text__iregex=".*\m(%s)\y.*"
                                                              % search)
                                               | Q(connection__contact__reporting_location__name__iregex=".*\m(%s)\y.*"
                                                                                                         % search)
                                               | Q(connection__pk__iregex=".*\m(%s)\y.*"
                                                                          % search))
        elif search[0] == "'" and search[-1] == "'":

            search = search[1:-1]
            message_list = message_list.filter(Q(text__iexact=search)
                                               | Q(connection__contact__reporting_location__name__iexact=search)
                                               | Q(connection__pk__iexact=search))
        elif search == "=numerical value()":
            message_list = message_list.filter(text__iregex="(-?\d+(\.\d+)?)")
        else:

            message_list = message_list.filter(Q(text__icontains=search)
                                               | Q(connection__contact__reporting_location__name__icontains=search)
                                               | Q(connection__pk__icontains=search))

    if request.GET.get('capture', None):
        (s, _) = Settings.objects.get_or_create(attribute='alerts')
        if s.value == 'true':
            s.value = 'false'
            s.save()
            reply = 'Start Capture'
        else:
            s.value = 'true'
            s.save()
            reply = 'Stop Capture'
        return HttpResponse(reply)
    if request.GET.get('ajax', None):
        date = datetime.datetime.now() - datetime.timedelta(seconds=30)
        prev = request.session.get('prev', [])
        msgs = Message.objects.filter(details__attribute__name='alert',
                                      direction='I'
        ).filter(date__gte=date).exclude(pk__in=prev)
        if access:
            msgs = msgs.filter(connection__contact__groups__in=access.groups.all())
        request.session['prev'] = list(msgs.values_list('pk',
                                                        flat=True))
        msgs_list = []
        if msgs:
            for msg in msgs:
                from django.template.loader import render_to_string

                can_view_number = request.user.has_perm('view_numbers')
                can_foward = request.user.has_perm('forward')
                row_rendered = \
                    render_to_string('ureport/partials/row.html',
                                     {'msg': msg, 'can_foward': can_foward, 'can_view_number': can_view_number,
                                      'assign_polls': assign_polls})

                m = {}
                m['text'] = msg.text
                m['date'] = str(msg.date.date())
                if msg.connection.contact:
                    m['name'] = msg.connection.contact.name
                else:
                    m['name'] = 'Anonymous User'
                m['number'] = msg.connection.identity
                if msg.connection.contact \
                    and msg.connection.contact.reporting_location:
                    m['district'] = \
                        msg.connection.contact.reporting_location.name
                else:
                    m['district'] = 'N/A'
                rating = msg.details.filter(attribute__name='alerts')
                if rating:
                    r = rating[0].value
                else:
                    r = 0
                m['row'] = row_rendered
                m['connection'] = msg.connection.pk
                m['pk'] = msg.pk
                msgs_list.append(m)
            return HttpResponse(mark_safe(simplejson.dumps(msgs_list)))
        else:
            return HttpResponse('success')
    if request.GET.get('rating', None):
        rating = request.GET.get('rating')
        descs = {
            '1': 'Requires Attention',
            '2': 'Moderate',
            '3': 'Important',
            '4': 'Urgent',
            '5': 'Very Urgent',
        }
        msg = Message.objects.get(pk=int(request.GET.get('msg')))
        (rate, _) = MessageAttribute.objects.get_or_create(name='rating'
        )
        det = MessageDetail.objects.create(message=msg, attribute=rate,
                                           value=rating, description=descs.get(rating, ''))
        response = \
            """<li><a href='javascript:void(0)'  class="rate%s"

                            title="%s">%s</a></li>""" \
            % (rating, descs.get(rating, ''), descs.get(rating, ''))

        return HttpResponse(mark_safe(response))

    paginator = UreportPaginator(message_list.order_by('-date'), 10, body=12, padding=2)
    page = request.GET.get('page', 1)
    try:
        messages = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):

        # If page is not an integer, deliver first page.

        messages = paginator.page(1)

    return render_to_response(template, {
        'messages': messages,
        'assign_polls': assign_polls,
        'paginator': paginator,
        'capture_status': capture_status,
        'rate': rate,
        'district_form': district_form,
        'range_form': range_form,
        'groupform': groupform,
    }, context_instance=RequestContext(request))


def remove_captured_ind(request, pk):
    msg = Message.objects.get(pk=pk)
    ma = MessageDetail.objects.filter(message=msg).delete()
    return HttpResponse(status=200)


def assign_poll(request, pk, poll):
    message = Message.objects.get(pk=pk)
    poll = Poll.objects.get(pk=poll)
    poll.process_response(message)
    return HttpResponse(status=200)


@login_required
def remove_captured(request):
    range_form = rangeForm(request.POST)
    if range_form.is_valid():
        start = range_form.cleaned_data['startdate']
        end = range_form.cleaned_data['enddate']
        message_list = \
            Message.objects.filter(details__attribute__name='alert'
            ).filter(date__range=(start, end))
        alert = MessageAttribute.objects.get(name='alert')
        mesg_details = \
            MessageDetail.objects.filter(message__in=message_list,
                                         attribute=alert).delete()
        return HttpResponse('success')

    return HttpResponse('Sucessfully deleted')


@login_required
def aids_dashboard(request):
    select_poll = SelectPoll()
    poll_form = NewPollForm()
    range_form = rangeForm()
    poll_form.updateTypes()
    template = 'ureport/aids_dashboard.html'

    (capture_status, _) = \
        Settings.objects.get_or_create(attribute='aids')
    (rate, _) = MessageAttribute.objects.get_or_create(name='rating')
    flag = Flag.objects.get(name="HIV")
    messages = flag.get_messages().order_by('-date')

    if request.GET.get('download', None):
        export_data = messages.values_list('connection__pk', 'text', 'connection__identity',
                                           'connection__contact__reporting_location__name').iterator()
        return ExcelResponse(data=export_data)
    if request.GET.get('capture', None):
        (s, _) = Settings.objects.get_or_create(attribute='aids')
        if s.value == 'true':
            s.value = 'false'
            s.save()
            reply = 'Start Capture'
        else:
            s.value = 'true'
            s.save()
            reply = 'Stop Capture'
        return HttpResponse(reply)
    if request.GET.get('ajax', None):
        date = datetime.datetime.now() - datetime.timedelta(seconds=30)
        prev = request.session.get('prev', [])
        msgs = flag.get_messages().filter(date__gte=date).exclude(pk__in=prev)
        request.session['prev'] = list(msgs.values_list('pk',
                                                        flat=True))
        msgs_list = []
        if msgs:
            for msg in msgs:
                from django.template.loader import render_to_string

                row_rendered = \
                    render_to_string('ureport/partials/row.html',
                                     {'msg': msg})

                m = {}
                m['text'] = msg.text
                m['date'] = str(msg.date.date())
                if msg.connection.contact:
                    m['name'] = msg.connection.contact.name
                else:
                    m['name'] = 'Anonymous User'
                m['number'] = msg.connection.identity
                if msg.connection.contact \
                    and msg.connection.contact.reporting_location:
                    m['district'] = \
                        msg.connection.contact.reporting_location.name
                else:
                    m['district'] = 'N/A'
                rating = msg.details.filter(attribute__name='aids')
                if rating:
                    r = rating[0].value
                else:
                    r = 0
                m['row'] = row_rendered
                m['connection'] = msg.connection.pk
                m['pk'] = msg.pk
                msgs_list.append(m)
            return HttpResponse(mark_safe(simplejson.dumps(msgs_list)))
        else:
            return HttpResponse('success')
    if request.GET.get('rating', None):
        rating = request.GET.get('rating')
        descs = {
            '1': 'Requires Attention',
            '2': 'Moderate',
            '3': 'Important',
            '4': 'Urgent',
            '5': 'Very Urgent',
        }
        msg = Message.objects.get(pk=int(request.GET.get('msg')))
        (rate, _) = MessageAttribute.objects.get_or_create(name='rating'
        )
        det = MessageDetail.objects.create(message=msg, attribute=rate,
                                           value=rating, description=descs.get(rating, ''))
        response = \
            """<li><a href='javascript:void(0)'  class="rate%s"

        title="%s">%s</a></li>""" \
            % (rating, descs.get(rating, ''), descs.get(rating, ''))

        return HttpResponse(mark_safe(response))

    paginator = UreportPaginator(messages, 10, body=12, padding=2)
    page = request.GET.get('page', 1)
    try:
        messages = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):

        # If page is not an integer, deliver first page.

        messages = paginator.page(1)

    return render_to_response(template, {
        'messages': messages,
        'paginator': paginator,
        'capture_status': capture_status,
        'rate': rate,
        'range_form': range_form,
    }, context_instance=RequestContext(request))


def schedule_alerts(request):
    mps = Contact.objects.filter(groups__name="MP")

    render_to_response("mp_alerts.html", dict(), context_instance=RequestContext(request))



