from rapidsms.models import Contact
from poll.models import Poll
from django.db.models import Count

def get_contacts():
    return Contact.objects.annotate(Count('responses'))

def get_polls():
    return Poll.objects.annotate(Count('responses'))

def retrieve_poll(request):
    pks=request.GET.get('pks', '').split('+')
    if pks[0] == 'l':
        return [Poll.objects.latest('start_date')]
    else:
        pks=[eval(x) for x in list(str(pks[0]).rsplit())]
        return Poll.objects.filter(pk__in=pks)
        