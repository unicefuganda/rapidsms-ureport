from rapidsms.models import Contact
from django.db.models import Count

def get_contacts():
    return Contact.objects.annotate(Count('responses'))

    