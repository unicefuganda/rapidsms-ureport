#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import date, timedelta

import re

from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import Group, User
from django.conf import settings
from django.contrib.sites.models import Site
from django.forms.widgets import RadioSelect
from django.forms import ValidationError
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext

from rapidsms.models import Contact
from poll.models import Poll, Response
from mptt.forms import TreeNodeChoiceField
from generic.forms import ActionForm, FilterForm, ModuleForm
from rapidsms.contrib.locations.models import Location
from poll.forms import NewPollForm
from rapidsms_httprouter.models import Message, Connection
from uganda_common.forms import SMSInput
from contact.models import MassText
from poll.models import Translation
from unregister.models import Blacklist
from .models import AutoregGroupRules, UploadContacts
from uganda_common.utils import ExcelResponse, assign_backend
from ureport.models import MessageAttribute, MessageDetail, Ureporter
from uganda_common.models import Access
import tasks
from ureport.utils import get_access


class EditReporterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditReporterForm, self).__init__(*args, **kwargs)
        self.fields['reporting_location'] = \
            TreeNodeChoiceField(queryset=self.fields['reporting_location'
            ].queryset.filter(type="district"), level_indicator=u'')


    class Meta:
        model = Contact
        fields = ['gender', 'birthdate', 'reporting_location', 'village_name', 'groups', 'language']


class EditUreporterForm(forms.Form):
    gender = forms.CharField(required=False)
    birthdate = forms.DateTimeField(required=False)
    reporting_location = forms.ModelChoiceField(Location.objects.filter(type='district'))
    village_name = forms.CharField(required=False)
    groups = forms.ModelMultipleChoiceField(Group.objects.all(), required=False)
    language = forms.ChoiceField(choices=(('en', 'en'), ('luo', 'luo', 'language')), required=False)

    def save(self, reporter):
        ureporter = Ureporter.objects.get(pk=reporter.pk)
        reporter.gender  = ureporter.gender= self.cleaned_data['gender']
        reporter.birthdate = ureporter.birhdate = self.cleaned_data['birthdate']
        reporter.reporting_location = ureporter.reporting_location = self.cleaned_data['reporting_location']
        reporter.village_name = ureporter.village_name = self.cleaned_data['village_name']
        reporter.language = ureporter.language = self.cleaned_data['language']
        reporter.save()
        ureporter.save()
        for group in self.cleaned_data['groups']:
            reporter.groups.add(group)
            ureporter.groups.add(group)


class PollModuleForm(ModuleForm):
    viz_type = forms.ChoiceField(choices=(
        ('ureport.views.show_timeseries', 'Poll responses vs time'),
        ('ureport.views.mapmodule', 'Map'),
        ('histogram', 'Histogram'),
        ('ureport.views.piegraph_module', 'Pie chart'),
        ('ureport.views.tag_cloud', 'Tag cloud'),
        ('poll-responses-module', 'Responses list'),
        ('poll-report-module', 'Tabular report'),
        ('best-viz', 'Results'),
        ('ureport.views.message_feed', 'Message Feed'),
    ), label='Poll visualization')
    poll = forms.ChoiceField(choices=(('l', 'Latest Poll'), )
                                     + tuple([(int(p.pk), str(p)) for p in
                                              Poll.objects.all().order_by('-start_date'
                                              )]), required=True)

    def setModuleParams(
            self,
            dashboard,
            module=None,
            title=None,
    ):
        title_dict = {
            'ureport.views.show_timeseries': 'Poll responses vs time',
            'ureport.views.mapmodule': 'Map',
            'histogram': 'Histogram',
            'ureport.views.piegraph_module': 'Pie chart',
            'ureport.views.tag_cloud': 'Tag cloud',
            'poll-responses-module': 'Responses list',
            'poll-report-module': 'Tabular report',
            'best-viz': 'Results',
            'ureport.views.message_feed': 'Message Feed',
        }
        viz_type = self.cleaned_data['viz_type']
        title = title_dict[viz_type]
        module = module or self.createModule(dashboard, viz_type,
                                             title=title)
        is_url_param = viz_type in ['poll-responses-module',
                                    'poll-report-module']
        if is_url_param:
            param_name = 'poll_id'
        else:
            param_name = 'pks'
        param_value = str(self.cleaned_data['poll'])
        module.params.create(module=module, param_name=param_name,
                             param_value=param_value,
                             is_url_param=is_url_param)
        return module


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Contacts Excel File',
                                 required=False)
    assign_to_group = \
        forms.ModelChoiceField(queryset=Group.objects.all(),
                               required=False)

    #    def __init__(self, data=None, **kwargs):
    #        self.request=kwargs.pop('request')
    #        if data:
    #            forms.Form.__init__(self, data, **kwargs)
    #        else:
    #            forms.Form.__init__(self, **kwargs)
    #        if hasattr(Contact, 'groups'):
    #            if self.request.user.is_authenticated():
    #                self.fields['assign_to_group'] = forms.ModelChoiceField(queryset=Group.objects.filter(pk__in=self.request.user.groups.values_list('pk',flat=True)), required=False)
    #            else:
    #                self.fields['assign_to_group'] = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)

    def clean(self):
        excel = self.cleaned_data.get('excel_file', None)
        if excel and excel.name.rsplit('.')[1] != 'xls':
            msg = u'Upload valid excel file !!!'
            self._errors['excel_file'] = ErrorList([msg])
            return ''
        return self.cleaned_data


class SearchResponsesForm(FilterForm):
    """ search responses
    """

    search = forms.CharField(max_length=100, required=True,
                             label='search Responses')

    def filter(self, request, queryset):
        search = self.cleaned_data['search'].strip()
        if search == '':
            return queryset

        elif search[0] == "'" and search[-1] == "'":

            search = search[1:-1]
            return queryset.filter(Q(message__text__iexact=search)
                                   | Q(message__connection__contact__reporting_location__name__iexact=search)
                                   | Q(message__connection__pk__iexact=search))
        elif search == "=numerical value()":
            return queryset.filter(message__text__iregex="(-?\d+(\.\d+)?)")
        else:

            return queryset.filter(Q(message__text__icontains=search)
                                   | Q(message__connection__contact__reporting_location__name__icontains=search)
                                   | Q(message__connection__pk__icontains=search))


class SearchMessagesForm(FilterForm):
    """ search messages
    """

    search = forms.CharField(max_length=100, required=True,
                             label='search ')

    def filter(self, request, queryset):

        search = self.cleaned_data['search'].strip()
        if search == '':
            return queryset
        elif search[0] == '"' and search[-1] == '"':
            search = search[1:-1]
            return queryset.filter(Q(text__iregex=".*\m(%s)\y.*"
                                                  % search)
                                   | Q(connection__contact__reporting_location__name__iregex=".*\m(%s)\y.*"
                                                                                             % search)
                                   | Q(connection__pk__iregex=".*\m(%s)\y.*"
                                                              % search))

        elif search == "'=numerical value()'":
            return queryset.filter(text__iregex="^[0-9]+$")

        elif search[0] == "'" and search[-1] == "'":

            search = search[1:-1]
            return queryset.filter(Q(text__iexact=search)
                                   | Q(connection__contact__reporting_location__name__iexact=search)
                                   | Q(connection__pk__iexact=search))
        elif search == "=numerical value()":
            return queryset.filter(text__iregex="(-?\d+(\.\d+)?)")
        else:

            return queryset.filter(Q(text__icontains=search)
                                   | Q(connection__contact__reporting_location__name__icontains=search)
                                   | Q(connection__pk__icontains=search))


class AssignToPollForm(ActionForm):
    """ assigns responses to poll  """

    poll = \
        forms.ModelChoiceField(queryset=Poll.objects.all().order_by('-pk'
        ), label=_('Poll'))
    action_label = _('Assign selected to poll')

    def perform(self, request, results):
        poll = self.cleaned_data['poll']
        for c in results:
            c.categories.all().delete()
            c.poll = poll
            c.save()
        return (
            _('%(length)d responses assigned to  %(poll)s poll') % {"length": len(results), "poll": poll.name},
            'success')


class DeleteSelectedForm(ActionForm):
    """ Deletes selected stuff  """

    action_label = _('Delete Selected')
    action_class = 'delete'

    def perform(self, request, results):
        count = len(results)
        if not count:
            return _('No contacts selected', 'error')

        if isinstance(results[0], QuerySet):
            results.delete()
        else:
            for object in results:
                object.delete()

        return ('%d  objects successfuly deleted ' % count, 'success')


class AssignToNewPollForm(ActionForm):
    """ assigns contacts to poll"""

    action_label = _('Assign to New poll')
    poll_name = forms.CharField(label=_('Poll Name'), max_length='100')
    POLL_TYPES = [('yn', _('Yes/No Question'))] + [(c['type'], c['label'])
                                                   for c in Poll.TYPE_CHOICES.values()]
    response_type = \
        forms.ChoiceField(choices=Poll.RESPONSE_TYPE_CHOICES,
                          widget=RadioSelect, label=_("Response type"))
    poll_type = forms.ChoiceField(choices=POLL_TYPES, label=_("Poll type"))
    question = forms.CharField(max_length=160, required=True, widget=SMSInput(), label=_("Question"))
    default_response = forms.CharField(max_length=160, required=False, widget=SMSInput(), label=_("Default response"))


    def perform(self, request, results):
        if not len(results):
            return (_('No contacts selected'), 'error')
        name = self.cleaned_data['poll_name']
        poll_type = self.cleaned_data['poll_type']
        poll_type = self.cleaned_data['poll_type']
        if poll_type == NewPollForm.TYPE_YES_NO:
            poll_type = Poll.TYPE_TEXT

        question = self.cleaned_data.get('question').replace('%',
                                                             u'\u0025')
        default_response = self.cleaned_data['default_response']
        response_type = self.cleaned_data['response_type']
        contacts = Contact.objects.filter(pk__in=results)
        poll = Poll.create_with_bulk(
            name=name,
            type=poll_type,
            question=question,
            default_response=default_response,
            contacts=contacts,
            user=request.user
        )

        poll.response_type = response_type
        if self.cleaned_data['poll_type'] == NewPollForm.TYPE_YES_NO:
            poll.add_yesno_categories()
        poll.save()

        if settings.SITE_ID:
            poll.sites.add(Site.objects.get_current())

        return (
            _('%(results)d participants added to  %(poll)s poll') % {"results": len(results), "poll": poll.name},
            'success')


DISTRICT_CHOICES = tuple([(int(d.pk), d.name) for d in
                          Location.objects.filter(type__slug='district'
                          ).order_by('name')])
phone_re = re.compile(r'(\d+)')


class SignupForm(forms.Form):
    firstname = forms.CharField(max_length=100, label='First Name')
    lastname = forms.CharField(max_length=100, label='Last Name')
    district = forms.ChoiceField(choices=DISTRICT_CHOICES,
                                 label='District')
    village = forms.CharField(label='Village', required=False)
    mobile = forms.CharField(label='Mobile Number', max_length=13,
                             required=True)
    gender = forms.ChoiceField(choices=(('M', 'Male'), ('F',
                                                        'Female')), label='Sex')
    group = forms.CharField(max_length=100, required=False,
                            label='How did you hear about U-report?')
    age = forms.IntegerField(max_value=100, min_value=10,
                             required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['district'] = \
            Location.objects.get(pk=int(cleaned_data.get('district', '1'
            )))
        try:
            phone = cleaned_data.get('mobile')
            p, b = assign_backend(phone)
        except Exception as e:
            raise ValidationError(str(e))
        return cleaned_data


class ReplyTextForm(ActionForm):
    text = forms.CharField(required=True, widget=SMSInput(), label=_("Text"))
    action_label = _('Reply to selected')

    def perform(self, request, results):
        if results is None or len(results) == 0:
            return (_('A message must have one or more recipients!'),
                    _('error'))

        if request.user and request.user.has_perm('contact.can_message'
        ):
            text = self.cleaned_data['text']
            if isinstance(results[0], Message):
                connections = results.values_list('connection',
                                                  flat=True)
            elif isinstance(results[0], Response):
                connections = results.values_list('message__connection'
                    , flat=True)

            Message.mass_text(text,
                              Connection.objects.filter(pk__in=connections).distinct(),
                              status='P', batch_status='Q', batch_name=None, priority=10)

            return ('%d messages sent successfully' % results.count(),
                    'success')
        else:
            return ("You don't have permission to send messages!",
                    'error')


class MassTextForm(ActionForm):
    text = forms.CharField(max_length=160, required=True, widget=SMSInput(), label=_("text"))
    text_luo = forms.CharField(max_length=160, required=False, widget=SMSInput(), label=_("text luo"))

    action_label = 'Send Message'

    def perform(self, request, results):
        if results is None or len(results) == 0:
            return (_('A message must have one or more recipients!'), 'error')

        if request.user and request.user.has_perm('contact.can_message'):
            blacklists = Blacklist.objects.values_list('connection')
            connections = \
                Connection.objects.filter(contact__in=results).exclude(pk__in=blacklists).distinct()

            text = self.cleaned_data.get('text', "")
            text = text.replace('%', u'\u0025')

            if not self.cleaned_data['text_luo'] == '':
                (translation, created) = \
                    Translation.objects.get_or_create(language='ach',
                                                      field=self.cleaned_data['text'],
                                                      value=self.cleaned_data['text_luo'])

            messages = Message.mass_text(text, connections)
            contacts = Contact.objects.filter(pk__in=results)

            MassText.bulk.bulk_insert(send_pre_save=False,
                                      user=request.user,
                                      text=text,
                                      contacts=list(contacts))
            masstexts = MassText.bulk.bulk_insert_commit(send_post_save=False, autoclobber=True)
            masstext = masstexts[0]

            return (
                _('Message successfully sent to %(connections)d numbers') % {"connections": len(connections)},
                'success',)
        else:
            return (_("You don't have permission to send messages!"), 'error',)


class NewPollForm(forms.Form): # pragma: no cover

    TYPE_YES_NO = 'yn'

    type = forms.ChoiceField(required=True, label=_("Type"), choices=((TYPE_YES_NO, _('Yes/No Question')),))
    response_type = forms.ChoiceField(choices=Poll.RESPONSE_TYPE_CHOICES, widget=RadioSelect,
                                      initial=Poll.RESPONSE_TYPE_ALL, label=_("Response type"))

    is_urgent = forms.BooleanField(required=False, label=_('Is urgent'))

    def updateTypes(self):
        self.fields['type'].widget.choices += [(choice['type'], choice['label']) for choice in
                                               Poll.TYPE_CHOICES.values()]

    name = forms.CharField(max_length=32, required=True, label=_('Name'))
    question_en = forms.CharField(max_length=160, required=True, widget=SMSInput(), label=_('Question en'))
    question_luo = forms.CharField(max_length=160, required=False, widget=SMSInput(), label=_('Question luo'))
    question_kdj = forms.CharField(max_length=160, required=False, widget=SMSInput(), label=_('Question kdj'))
    default_response_en = forms.CharField(max_length=160, required=False, widget=SMSInput(),
                                          label=_('Default response en'))
    default_response_kdj = forms.CharField(max_length=160, required=False, widget=SMSInput(),
                                           label=_('Default response kdj'))
    districts = forms.ModelMultipleChoiceField(queryset=Location.objects.filter(type__slug='district').order_by('name'),
                                               required=False, label=_('districts'))
    default_response_luo = forms.CharField(max_length=160, required=False, widget=SMSInput(),
                                           label=_('Default response luo'))

    # This may seem like a hack, but this allows time for the Contact model
    # to optionally have groups (i.e., poll doesn't explicitly depend on the rapidsms-auth
    # app.
    def __init__(self, data=None, **kwargs):
        queryset = Group.objects.order_by('name')
        if 'request' in kwargs:
            request = kwargs.pop('request')
        if data:
            forms.Form.__init__(self, data, **kwargs)
        else:
            forms.Form.__init__(self, **kwargs)
        try:
            access = Access.objects.get(user=request.user)
            queryset = access.groups.order_by('name')
        except Access.DoesNotExist:
            pass
        except UnboundLocalError:
            pass
        if hasattr(Contact, 'groups'):
            self.fields['groups'] = forms.ModelMultipleChoiceField(queryset=queryset, required=False, label=_('groups'))

    def clean(self):
        cleaned_data = self.cleaned_data
        groups = cleaned_data.get('groups')
        if cleaned_data.get('question_en', None):
            cleaned_data['question_en'] = cleaned_data.get('question_en').replace('%', u'\u0025')
        if cleaned_data.get('default_response_en', None):
            cleaned_data['default_response_en'] = cleaned_data['default_response_en'].replace('%', u'\u0025')

        if not groups:
            raise forms.ValidationError(_("You must provide a set of recipients (a group or groups)"))

        return cleaned_data

    def clean_default_response_en(self):
        return self._cleaned_default_response(self.data['default_response_en'])

    def clean_default_response_luo(self):
        return self._cleaned_default_response(self.data['default_response_luo'])

    def clean_default_response_kdj(self):
        return self._cleaned_default_response(self.cleaned_data['default_response_kdj'])

    def _cleaned_default_response(self, default_response):
        return default_response.replace('%', '%%')


class AssignResponseGroupForm(ActionForm):
    action_label = 'Assign to group(s)'

    # This may seem like a hack, but this allows time for the Contact model's
    # default manage to be replaced at run-time.  There are many applications
    # for that, such as filtering contacts by site_id (as is done in the
    # authsites app, see github.com/daveycrockett/authsites).
    # This does, however, also make the polling app independent of authsites.
    def __init__(self, data=None, **kwargs):
        self.request = kwargs.pop('request')
        self.access = None
        if 'access' in kwargs:
            self.access = kwargs.pop('access')
        if data:
            forms.Form.__init__(self, data, **kwargs)
        else:
            forms.Form.__init__(self, **kwargs)
        if hasattr(Contact, 'groups'):
            if self.request.user.is_authenticated():
                self.fields['groups'] = forms.ModelMultipleChoiceField(
                    queryset=Group.objects.filter(pk__in=self.request.user.groups.values_list('pk', flat=True)),
                    required=False, label=_('Groups'))
            else:
                self.fields['groups'] = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
            if self.access:
                self.fields['groups'] = forms.ModelChoiceField(queryset=self.access.groups.all())

    def perform(self, request, results):
        groups = self.cleaned_data['groups']

        for response in results:
            for g in groups:
                contact = response.message.connection.contact
                if contact:
                    contact.groups.add(g)
        return ('%d Contacts assigned to %d groups.' % (len(results), len(groups)), 'success',)


class BlacklistForm2(ActionForm):
    """ abstract class for all the filter forms"""
    action_label = _('Blacklist/Opt-out Users')

    def perform(self, request, results):
        if request.user and request.user.has_perm('unregister.add_blacklist'):

            connections = Connection.objects.filter(pk__in=results.values_list('connection')).distinct()
            for c in connections:
                Blacklist.objects.get_or_create(connection=c)
                Message.objects.create(status="Q", direction="O", connection=c,
                                       text="Your UReport opt out is confirmed.If you made a mistake,or you want your voice to be heard again,text in JOIN and send it to 8500!All SMS messages are free")
            return ('You blacklisted %d numbers' % len(connections), 'success',)
        else:
            return ("You don't have permissions to blacklist numbers", 'error',)


class SelectPoll(forms.Form):
    """ filter responses to poll  """

    poll = \
        forms.ModelChoiceField(queryset=Poll.objects.exclude(start_date=None).order_by('-pk'))


class SelectCategory(forms.Form):
    category = \
        forms.ModelMultipleChoiceField(queryset=QuerySet())

    def __init__(self, *args, **kwargs):
        categories = kwargs['categories']
        del kwargs['categories']
        super(SelectCategory, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = categories


class SendMessageForm(forms.Form):
    recipients = forms.CharField(label="recepient(s)", required=True, help_text="enter numbers commas separated",
                                 widget=forms.HiddenInput)
    text = forms.CharField(required=True, widget=SMSInput())


class ForwardMessageForm(forms.Form):
    recipients = forms.CharField(label="recepient(s)", required=True,
                                 help_text="enter commas separated numbers or emails")
    text = forms.CharField(required=True, widget=SMSInput())


class rangeForm(forms.Form):
    startdate = forms.DateField(('%d/%m/%Y',), label=_('Start Date'), required=False,
                                widget=forms.DateTimeInput(format='%d/%m/%Y', attrs={
                                    'class': 'input',
                                    'readonly': 'readonly',
                                    'size': '15'
                                }))
    enddate = forms.DateField(('%d/%m/%Y',), label=_('End Date'), required=False,
                              widget=forms.DateTimeInput(format='%d/%m/%Y', attrs={
                                  'class': 'input',
                                  'readonly': 'readonly',
                                  'size': '15'
                              }))


class GroupRules(forms.ModelForm):
    class Meta:
        model = AutoregGroupRules
        exclude = ('rule_regex',)


class DownloadForm(forms.Form):
    startdate = forms.DateField(('%d/%m/%Y',), label=_('Start Date'), required=False,
                                widget=forms.DateTimeInput(format='%d/%m/%Y', attrs={
                                    'class': 'input',
                                    'readonly': 'readonly',
                                    'size': '15'
                                }))
    enddate = forms.DateField(('%d/%m/%Y',), label=_('End Date'), required=False,
                              widget=forms.DateTimeInput(format='%d/%m/%Y', attrs={
                                  'class': 'input',
                                  'readonly': 'readonly',
                                  'size': '15'
                              }))

    def export(self, request, queryset, date_field):
        if request.user.has_perm("ureport.can_export"):
            start = self.cleaned_data['startdate']
            end = self.cleaned_data['enddate']
            date = "%s__range" % date_field
            kwargs = dict(date=(start, end))
            data = queryset.filter(**kwargs).values()
            response = ExcelResponse(data=list(data))
            return response


class UreporterSearchForm(FilterForm):
    """ concrete implementation of filter form
        TO DO: add ability to search for multiple search terms separated by 'or'
    """

    searchx = forms.CharField(max_length=100, required=False, label="Free-form search",
                              help_text="Use 'or' to search for multiple names")

    def filter(self, request, queryset):
        searchx = self.cleaned_data['searchx'].strip()
        if searchx == "":
            return queryset
        elif searchx[0] in ["'", '"'] and searchx[-1] in ["'", '"']:
            searchx = searchx[1:-1]
            return queryset.filter(Q(district__iregex=".*\m(%s)\y.*" % searchx)
                                   | Q(connection_pk__icontains=".*\m(%s)\y.*" % searchx))

        else:
            return queryset.filter(Q(district__icontains=searchx)
                                   | Q(connection_pk=searchx))


class AgeFilterForm(FilterForm):
    """ filter contacts by their age """
    flag = forms.ChoiceField(label='', choices=(('', '-----'), ('==', _('Equal to')), ('>', _('Greater than')),
                                                ('<', _('Less than')),
                                                ('None', 'N/A')), required=False)
    age = forms.CharField(max_length=20, label="Age", widget=forms.TextInput(attrs={'size': '20'}), required=False)

    def filter(self, request, queryset):

        flag = self.cleaned_data['flag']

        try:
            age = int(self.cleaned_data['age'])
        except:
            age = None

        if flag == '':
            return queryset
        elif flag == '==':
            return queryset.filter(age=age)
        elif flag == '>':
            return queryset.filter(age__gte=age)
        elif flag == "<":
            return queryset.filter(age__lte=age)
        else:
            return queryset.filter(age=None)


class DistrictForm(forms.Form):
    districts = forms.ModelMultipleChoiceField(queryset=Location.objects.filter(type__slug='district').order_by('name'),
                                               required=True, label=_("Districts"))


def get_poll_data(poll):
    yesno_category_names = ['yes', 'no']
    if poll.categories.count():
        category_names = yesno_category_names if poll.is_yesno_poll() else list(
            poll.categories.all().values_list('name', flat=True))
        root = Location.tree.root_nodes()[0]
        data = poll.responses_by_category(root)
        clean_data = {}
        for d in data:
            l = Location.objects.get(pk=d['location_id'])
            clean_data.setdefault(l.pk, {})
            clean_data[l.pk][d['category__name']] = d['value']

        for district_code, values in clean_data.items():
            total = 0
            for c in category_names:
                values.setdefault(c, 0)
            for cat_name, val in values.items():
                total += val
            for cat_name in category_names:
                values[cat_name] = '%d%% ' % int(float(values[cat_name]) * 100 / total)

        return clean_data
    return None


def get_summary(pk, poll_data):
    c = poll_data.get(pk, None)
    return " ".join(["%s said %s" % ( str(c[a]), str(a)) for a in c.keys() if not a in ["uncategorized", "unknown"]])


class TemplateMessage(ActionForm):
    template = forms.CharField(max_length=160, required=True, widget=SMSInput(), label=_("Template"),
                               help_text=_(
                                   "message shd be of form Dear Hon. [insert name]. [insert results ] of people from [insert district] say that lorem ipsum"))
    poll = forms.ModelChoiceField(
        queryset=Poll.objects.exclude(start_date=None).exclude(categories=None).order_by('-pk'), label=_("Poll"))

    label = "Send Message"


    def perform(self, request, results):

        if request.user:
            poll = self.cleaned_data['poll']
            contacts = Contact.objects.filter(pk__in=results).exclude(connection=None)
            regex = re.compile(r"(\[[^\[\]]+\])")
            template = self.cleaned_data['template']
            parts = regex.split(template)
            yesno_category_names = ['yes', 'no']
            poll_data = get_poll_data(poll)
            if poll_data:
                import datetime

                key = "templatemsg%s" % str(datetime.datetime.now().isoformat())
                temp_msg, _ = MessageAttribute.objects.get_or_create(name=key)

                for contact in contacts:

                    if contact.reporting_location and poll_data.get(contact.reporting_location.pk, None):
                        d = {
                            'name': contact.name.split()[-1],
                            'district': contact.reporting_location.name,
                            'results': get_summary(contact.reporting_location.pk, poll_data)

                        }

                        message = ""
                        for p in parts:
                            if p.strip().startswith("["):

                                message = message + d[p.replace("[", "").replace("]", "").strip().rsplit()[1]]
                            else:
                                message = message + p

                        message = Message.objects.create(status="P", direction="O",
                                                         connection=contact.default_connection, text=message)
                        msg_a = MessageDetail.objects.create(message=message, attribute=temp_msg, value='comfirm')

                message_final = ugettext("Message is going to be sent to %(contacts)d contacts.") % { 'contacts':len(results)}
                alert_message = ugettext("Confirm Sending")
                return mark_safe('%s<a href="/comfirmmessages/%s/">%s </a>' % (message_final, key, alert_message)), 'success'
                
            else:
                return ("some thing went wrong", 'error',)

        else:
            return ("you need to be logged in ", 'error',)


class GroupsFilter(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            request = kwargs.pop('request')
        super(GroupsFilter, self).__init__(*args, **kwargs)
        try:
            access = Access.objects.get(user=request.user)
            self.fields['group_list'] = forms.ModelMultipleChoiceField(queryset=access.groups.order_by('name'),
                                                                       required=False)
        except Access.DoesNotExist, e:
            self.fields['group_list'] = forms.ModelMultipleChoiceField(queryset=Group.objects.order_by('name'),
                                                                       required=False)
        except UnboundLocalError, e:
            print "UnboundLocalError:", e
            self.fields['group_list'] = forms.ModelMultipleChoiceField(queryset=Group.objects.order_by('name'),
                                                                       required=False)
        except Exception, e:
            print "General Exception: ", e
            self.fields['group_list'] = forms.ModelMultipleChoiceField(queryset=Group.objects.order_by('name'),
                                                                       required=False)


class PushToMtracForm(ActionForm):
    action_label = _("Push Selected Messages to Mtrac")

    def perform(self, request, results):
        results = set([r.pk for r in results])
        tasks.push_to_mtrac.delay(results)
        return _("%(count)d Messages were pushed to mtrac") % {'count': len(results)}, "success"


class UploadContactsForm(forms.ModelForm):
    class Meta:
        model = UploadContacts
        fields = ('excel_file',)

    @classmethod
    def process(cls, upload):
        tasks.process_uploaded_contacts.delay(upload)


class AssignGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    contacts = forms.FileField()

    def handle_upload(self, upload):
        from datetime import datetime

        path = '/tmp/' + str(datetime.now()).replace(" ", "_").replace("-", "_").replace(":", "_")
        with open(path, 'wb+') as excel_file:
            for chunk in upload.chunks():
                excel_file.write(chunk)
            excel_file.close()
        return path

    def process(self, upload, username):
        tasks.process_assign_group.delay(upload, self.cleaned_data['group'], username)


class SearchPollsForm(FilterForm):
    search_term = forms.CharField()

    def filter(self, request, queryset):
        return queryset.filter(Q(name__icontains=self.cleaned_data['search_term']) | Q(
            question__icontains=self.cleaned_data['search_term']))


class ExReportForm(forms.Form):
    ALL = 'A'
    UNSOLICITED = 'U'
    POLLED = 'P'

    MALE = 'M'
    FEMALE = 'F'

    required_css_class = 'required'

    GENDER_CHOICES = ((ALL, 'All'), (MALE, 'Male'), (FEMALE, 'Female'))

    FILTER_CHOICES = ((ALL, 'All'), (UNSOLICITED, 'Unsolicited Messages'), (POLLED, 'Polled Messages'))

    districts = forms.ModelMultipleChoiceField(queryset=Location.objects.filter(type='district'), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    age_from = forms.IntegerField(max_value=90, min_value=10,
                                  error_messages={'invalid': "Age must be a number between 10 and 90"}, required=True,
                                  widget=forms.TextInput(attrs={"style": "width: 24px"}))
    age_to = forms.IntegerField(max_value=90, min_value=10,
                                error_messages={'invalid': "Age must be a number between 10 and 90"}, required=True,
                                widget=forms.TextInput(attrs={"style": "width: 24px"}))
    date_from = forms.DateField()
    date_to = forms.DateField()
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    partner = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    filter = forms.ChoiceField(choices=FILTER_CHOICES)

    def extract(self, request):
        tasks.extract_gen_reports.delay(self.cleaned_data, username=request.user.username, host=request.get_host())
