from django import forms
from rapidsms.models import Contact,Connection
from django.db.models import Q
from django.forms.widgets import HiddenInput
from rapidsms.messages.outgoing import OutgoingMessage
from generic.forms import ActionForm, FilterForm
from poll.models import Poll, Response
from mptt.forms import TreeNodeChoiceField

class EditReporterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
           super(EditReporterForm, self).__init__(*args, **kwargs)
           self.fields['reporting_location'] = TreeNodeChoiceField(queryset=self.fields['reporting_location'].queryset,level_indicator=u'.')

    class Meta:
        model=Contact

class ReplyForm(forms.Form):        
    recipient = forms.CharField(max_length=20)
    message = forms.CharField(max_length=160, widget=forms.TextInput(attrs={'size':'60'}))
    in_response_to = forms.ModelChoiceField(queryset=Message.objects.filter(direction='I'), widget=forms.HiddenInput())
