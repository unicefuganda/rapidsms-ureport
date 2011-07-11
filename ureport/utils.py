from rapidsms.models import Contact
from poll.models import Poll
from django.db.models import Count

def get_contacts(**kwargs):
    request = kwargs.pop('request')
    if request.user.is_authenticated() and hasattr(Contact, 'groups'):
        return Contact.objects.filter(groups__in=request.user.groups.all()).annotate(Count('responses')) 
    else:
        return Contact.objects.annotate(Count('responses'))

def get_polls(**kwargs):
    return Poll.objects.annotate(Count('responses'))

#def retrieve_poll(request):
#    pks=request.GET.get('pks', '').split('+')
#    if pks[0] == 'l':
#        return [Poll.objects.latest('start_date')]
#    else:
#        pks=[eval(x) for x in list(str(pks[0]).rsplit())]
#        return Poll.objects.filter(pk__in=pks)

def retrieve_poll(request, pks=None):
    if pks == None:
        pks=request.GET.get('pks', '')
    if pks == 'l':
        return [Poll.objects.latest('start_date')]
    else:
        return Poll.objects.filter(pk__in=[pks])
    
        