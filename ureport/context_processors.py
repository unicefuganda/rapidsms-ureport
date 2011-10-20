"""A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.
"""
from rapidsms.models import Contact
from unregister.models import Blacklist
from poll.models import Poll
from django.conf import settings

def voices(request):
    """
    a context processor that passes the total number of ureporters to all templates.
    """
    return {
        'total_ureporters':Contact.objects.exclude(connection__identity__in=Blacklist.objects.values_list('connection__identity')).count(),
        'polls':Poll.objects.exclude(contacts=None, start_date=None).order_by('-start_date'),
       'deployment_id':settings.DEPLOYMENT_ID
        }



