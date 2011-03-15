from rapidsms.models import Contact
from poll.models import Poll
from django.db.models import Count

def get_contacts():
    return Contact.objects.annotate(Count('responses'))

def get_polls():
    return Poll.objects.annotate(Count('responses'))





    