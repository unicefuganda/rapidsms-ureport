from django import forms
from rapidsms.models import Contact,Connection
from status160.models import  Team
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