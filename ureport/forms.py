# -*- coding: utf-8 -*-
from django import forms
from rapidsms.models import Contact
from django.contrib.auth.models import Group
from poll.models import Poll
from mptt.forms import TreeNodeChoiceField
from generic.forms import ActionForm, FilterForm, ModuleForm
from django.conf import settings
from django.contrib.sites.models import Site
from django.forms.widgets import RadioSelect

class EditReporterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
           super(EditReporterForm, self).__init__(*args, **kwargs)
           self.fields['reporting_location'] = TreeNodeChoiceField(queryset=self.fields['reporting_location'].queryset, level_indicator=u'.')

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
    ), label="Poll visualization")
    poll = forms.ChoiceField(choices=(('l', 'Latest Poll'),) + tuple([(int(p.pk), str(p)) for p in Poll.objects.all().order_by('-start_date')]), required=True)

    def setModuleParams(self, dashboard, module=None, title=None):
        title_dict = {
            'ureport.views.show_timeseries':'Poll responses vs time',
            'ureport.views.mapmodule':'Map',
            'histogram':'Histogram',
            'ureport.views.piegraph_module':'Pie chart',
            'ureport.views.tag_cloud':'Tag cloud',
            'poll-responses-module':'Responses list',
            'poll-report-module':'Tabular report',
            'best-viz':'Results',
            'ureport.views.message_feed':'Message Feed',
        }
        viz_type = self.cleaned_data['viz_type']
        title = title_dict[viz_type]
        module = module or self.createModule(dashboard, viz_type, title=title)
        is_url_param = viz_type in ['poll-responses-module', 'poll-report-module']
        if is_url_param:
            param_name = 'poll_id'
        else:
            param_name = 'pks'
        param_value = str(self.cleaned_data['poll'])
        module.params.create(module=module, param_name=param_name, param_value=param_value, is_url_param=is_url_param)
        return module

class ExcelUploadForm(forms.Form):

    excel_file = forms.FileField(label="Contacts Excel File", required=False)
    assign_to_group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
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
                self._errors["excel_file"] = ErrorList([msg])
                return ''
        return self.cleaned_data

class SearchResponsesForm(FilterForm):

    """ search responses 
    """

    search = forms.CharField(max_length=100, required=True, label="search Responses")

    def filter(self, request, queryset):
        search = self.cleaned_data['search']
        return queryset.filter(message__text__icontains=search)


class AssignToPollForm(ActionForm):
    """ assigns responses to poll  """
    poll = forms.ModelChoiceField(queryset=Poll.objects.all().order_by('name'))
    action_label = 'Assign selected to poll'
    def perform(self, request, results):
        poll = self.cleaned_data['poll']
        for c in results:
            c.categories.all().delete()
            c.poll = poll
            c.save()
        return ('%d responses assigned to  %s poll' % (len(results), poll.name), 'success',)

class AssignToNewPollForm(ActionForm):
    """ assigns contacts to poll"""
    action_label = 'Assign to New poll'
    poll_name = forms.CharField(label="Poll Name", max_length="100")
    POLL_TYPES = [('yn', 'Yes/No Question')] + [(c['type'], c['label']) for c in Poll.TYPE_CHOICES.values()]
    response_type=forms.ChoiceField(choices=Poll.RESPONSE_TYPE_CHOICES,widget=RadioSelect)
    poll_type = forms.ChoiceField(choices=POLL_TYPES)
    question = forms.CharField(max_length=160, required=True)
    default_response = forms.CharField(max_length=160, required=False)
    start_immediately = forms.BooleanField(required=False)

    def perform(self, request, results):
        if not len(results):
            return ("No contacts selected", "error")
        name = self.cleaned_data['poll_name']
        poll_type = self.cleaned_data['poll_type']
        question = self.cleaned_data.get('question').replace('%', u'\u0025')
        default_response = self.cleaned_data['default_response']
        start_immediately = self.cleaned_data['start_immediately']
        response_type = self.cleaned_data['response_type']
        poll = Poll.create_with_bulk(\
                                 name=name,
                                 type=poll_type,
                                question=question,
                                 default_response=default_response,
                                 contacts=results,
                                 user=request.user)
        poll.response_type=response_type
        poll.save()

        if settings.SITE_ID:
            poll.sites.add(Site.objects.get_current())
        if start_immediately:
            poll.start()
        return ('%d participants added to  %s poll' % (len(results), poll.name), 'success',)

