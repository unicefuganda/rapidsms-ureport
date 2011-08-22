from django import forms
from rapidsms.models import Contact, Connection
from django.db.models import Q
from django.forms.widgets import HiddenInput
from django.contrib.auth.models import Group
from rapidsms.messages.outgoing import OutgoingMessage
from generic.forms import ActionForm, FilterForm
from poll.models import Poll, Response
from mptt.forms import TreeNodeChoiceField
from rapidsms_httprouter.models import Message
from generic.forms import ActionForm, FilterForm, ModuleForm
from django.forms.widgets import Select

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
    poll=forms.ModelChoiceField(queryset=Poll.objects.all().order_by('name'))
    action_label = 'Assign selected to poll'
    def perform(self, request, results):
        poll = self.cleaned_data['poll']
        for c in results:
            c.poll=poll
            c.poll.save()
            c.save()
        return ('%d responses assigned to  %s poll' % (results.count(), poll.name), 'success',)
