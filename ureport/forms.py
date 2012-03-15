#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from rapidsms.models import Contact
from django.contrib.auth.models import Group
from poll.models import Poll, Response
from mptt.forms import TreeNodeChoiceField
from generic.forms import ActionForm, FilterForm, ModuleForm
from django.conf import settings
from django.contrib.sites.models import Site
from django.forms.widgets import RadioSelect
from rapidsms.contrib.locations.models import Location
from django.forms import ValidationError
from django.db.models import Q
import re
from poll.forms import NewPollForm
from rapidsms_httprouter.models import Message, Connection
from uganda_common.forms import SMSInput
from django.db.models.query import QuerySet
from contact.models import MassText
from poll.models import Poll, Translation
from unregister.models import Blacklist

import subprocess


class EditReporterForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditReporterForm, self).__init__(*args, **kwargs)
        self.fields['reporting_location'] = \
            TreeNodeChoiceField(queryset=self.fields['reporting_location'
                                ].queryset, level_indicator=u'.')


    class Meta:

        model = Contact
        fields = ('name', 'reporting_location', 'groups')


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
        elif search[0] == '"' and search[-1] == '"':
            search = search[1:-1]
            return queryset.filter(Q(message__text__iregex=".*\m(%s)\y.*"
                                    % search)
                                   | Q(message__connection__contact__reporting_location__name__iregex=".*\m(%s)\y.*"
                                    % search)
                                   | Q(message__connection__identity__iregex=".*\m(%s)\y.*"
                                    % search))
        elif search[0] == "'" and search[-1] == "'":

            search = search[1:-1]
            return queryset.filter(Q(message__text__iexact=search)
                                   | Q(message__connection__contact__reporting_location__name__iexact=search)
                                   | Q(message__connection__identity__iexact=search))
        elif search == "=numerical value()":
            return queryset.filter(message__text__iregex="(-?\d+(\.\d+)?)")
        else:

            return queryset.filter(Q(message__text__icontains=search)
                                   | Q(message__connection__contact__reporting_location__name__icontains=search)
                                   | Q(message__connection__identity__icontains=search))


class AssignToPollForm(ActionForm):

    """ assigns responses to poll  """

    poll = \
        forms.ModelChoiceField(queryset=Poll.objects.all().order_by('-pk'
                               ))
    action_label = 'Assign selected to poll'

    def perform(self, request, results):
        poll = self.cleaned_data['poll']
        for c in results:
            c.categories.all().delete()
            c.poll = poll
            c.save()
        return ('%d responses assigned to  %s poll' % (len(results),
                poll.name), 'success')


class DeleteSelectedForm(ActionForm):

    """ Deletes selected stuff  """

    action_label = 'Delete Selected '
    action_class = 'delete'

    def perform(self, request, results):
        count = len(results)
        if not count:
            return ('No contacts selected', 'error')

        if isinstance(results[0], QuerySet):
            results.delete()
        else:
            for object in results:
                object.delete()

        return ('%d  objects successfuly deleted ' % count, 'success')


class AssignToNewPollForm(ActionForm):

    """ assigns contacts to poll"""

    action_label = 'Assign to New poll'
    poll_name = forms.CharField(label='Poll Name', max_length='100')
    POLL_TYPES = [('yn', 'Yes/No Question')] + [(c['type'], c['label'])
            for c in Poll.TYPE_CHOICES.values()]
    response_type = \
        forms.ChoiceField(choices=Poll.RESPONSE_TYPE_CHOICES,
                          widget=RadioSelect)
    poll_type = forms.ChoiceField(choices=POLL_TYPES)
    question = forms.CharField(max_length=160, required=True)
    default_response = forms.CharField(max_length=160, required=False)


    def perform(self, request, results):
        if not len(results):
            return ('No contacts selected', 'error')
        name = self.cleaned_data['poll_name']
        poll_type = self.cleaned_data['poll_type']
        poll_type = self.cleaned_data['poll_type']
        if poll_type == NewPollForm.TYPE_YES_NO:
            poll_type = Poll.TYPE_TEXT

        question = self.cleaned_data.get('question').replace('%',
                u'\u0025')
        default_response = self.cleaned_data['default_response']
        response_type = self.cleaned_data['response_type']
        poll = Poll.create_with_bulk(
            name=name,
            type=poll_type,
            question=question,
            default_response=default_response,
            contacts=results,
            user=request.user
            )

        poll.response_type = response_type
        if self.cleaned_data['poll_type'] == NewPollForm.TYPE_YES_NO:
            poll.add_yesno_categories()
        poll.save()

        if settings.SITE_ID:
            poll.sites.add(Site.objects.get_current())

        return ('%d participants added to  %s poll' % (len(results),
                poll.name), 'success')


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
    gender = forms.ChoiceField(choices=(('Male', 'Male'), ('Female',
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
        match = re.match(phone_re, cleaned_data.get('mobile', ''))
        if not match:
            raise ValidationError('invalid Number')
        return cleaned_data


class ReplyTextForm(ActionForm):

    text = forms.CharField(required=True, widget=SMSInput())
    action_label = 'Reply to selected'

    def perform(self, request, results):
        if results is None or len(results) == 0:
            return ('A message must have one or more recipients!',
                    'error')

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
                              status='P')

            return ('%d messages sent successfully' % results.count(),
                    'success')
        else:
            return ("You don't have permission to send messages!",
                    'error')

class MassTextForm(ActionForm):

    text = forms.CharField(max_length=160, required=True, widget=SMSInput())
    text_luo = forms.CharField(max_length=160, required=False, widget=SMSInput())
    action_label = 'Send Message'

    def perform(self, request, results):
        if results is None or len(results) == 0:
            return ('A message must have one or more recipients!', 'error')

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

            MassText.bulk.bulk_insert(send_pre_save=False,
                    user=request.user,
                    text=text,
                    contacts=list(results))
            masstexts = MassText.bulk.bulk_insert_commit(send_post_save=False, autoclobber=True)
            masstext = masstexts[0]
            
            return ('Message successfully sent to %d numbers' % len(connections), 'success',)
        else:
            return ("You don't have permission to send messages!", 'error',)

class NewPollForm(forms.Form): # pragma: no cover

    TYPE_YES_NO = 'yn'

    type = forms.ChoiceField(
               required=True,
               choices=(
                    (TYPE_YES_NO, 'Yes/No Question'),
                ))
    response_type=forms.ChoiceField(choices=Poll.RESPONSE_TYPE_CHOICES,widget=RadioSelect,initial=Poll.RESPONSE_TYPE_ALL)

    def updateTypes(self):
        self.fields['type'].widget.choices += [(choice['type'], choice['label']) for choice in Poll.TYPE_CHOICES.values()]

    name = forms.CharField(max_length=32, required=True)
    question = forms.CharField(max_length=160, required=True,widget=SMSInput())
    question_luo = forms.CharField(max_length=160, required=False,widget=SMSInput())
    default_response = forms.CharField(max_length=160, required=False,widget=SMSInput())
    default_response_luo = forms.CharField(max_length=160, required=False,widget=SMSInput())
    districts = forms.ModelMultipleChoiceField(queryset=
                                 Location.objects.filter(type__slug='district'
                                 ).order_by('name'), required=False)

    # This may seem like a hack, but this allows time for the Contact model
    # to optionally have groups (i.e., poll doesn't explicitly depend on the rapidsms-auth
    # app.
    def __init__(self, data=None, **kwargs):
        if data:
            forms.Form.__init__(self, data, **kwargs)
        else:
            forms.Form.__init__(self, **kwargs)
        if hasattr(Contact, 'groups'):
            self.fields['groups'] = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        groups = cleaned_data.get('groups')
        if cleaned_data.get('question',None):
            cleaned_data['question'] = cleaned_data.get('question').replace('%', u'\u0025')
        if cleaned_data.get('default_response',None):
            cleaned_data['default_response'] = cleaned_data['default_response'].replace('%', u'\u0025')

        if  not groups:
            raise forms.ValidationError("You must provide a set of recipients (a group or groups)")

        return cleaned_data