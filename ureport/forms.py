from django import forms
from rapidsms.models import Contact,Connection
from django.db.models import Q
from django.forms.widgets import HiddenInput
from rapidsms.messages.outgoing import OutgoingMessage
from generic.forms import ActionForm, FilterForm
from poll.models import Poll, Response
from mptt.forms import TreeNodeChoiceField
from rapidsms_httprouter.models import Message
from generic.forms import ActionForm, FilterForm, ModuleForm

class EditReporterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
           super(EditReporterForm, self).__init__(*args, **kwargs)
           self.fields['reporting_location'] = TreeNodeChoiceField(queryset=self.fields['reporting_location'].queryset,level_indicator=u'.')

    class Meta:
        model=Contact
        fields=('name','reporting_location','groups')

class ReplyForm(forms.Form):        
    recipient = forms.CharField(max_length=20)
    message = forms.CharField(max_length=160, widget=forms.TextInput(attrs={'size':'60'}))
    in_response_to = forms.ModelChoiceField(queryset=Message.objects.filter(direction='I'), widget=forms.HiddenInput())

class PollModuleForm(ModuleForm):
    viz_type=forms.ChoiceField(choices=(
        ('ureport.views.show_timeseries','Poll responses vs time'),
        ('ureport.views.mapmodule','Map'),
        ('histogram','Histogram'),
        ('ureport.views.piegraph_module','Pie chart'),
        ('ureport.views.tag_cloud','Tag cloud'),
        ('poll-responses-module','Responses list'),
        ('poll-report-module','Tabular report'),
        ('best-viz', 'Results'),
        ('ureport.views.message_feed', 'Message Feed'),
    ), label="Poll visualization")
    poll = forms.ChoiceField(choices = (('l','Latest Poll'),) + tuple([(int(p.pk), str(p)) for p in Poll.objects.all().order_by('-start_date')]), required=True)

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
        is_url_param = viz_type in ['poll-responses-module','poll-report-module']
        if is_url_param:
            param_name = 'poll_id'
        else:
            param_name = 'pks'
        param_value = str(self.cleaned_data['poll'])
        module.params.create(module=module, param_name=param_name, param_value=param_value, is_url_param=is_url_param)
        return module
