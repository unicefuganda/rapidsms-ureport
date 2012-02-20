from django.core.management.base import BaseCommand
import re
from ussd.models import *
from poll.models import Poll

def get_results(poll):
    txt=""
    res=poll.responses_by_category()
    res_count=poll.responses.count()
    if poll.categories.all().exists():
        for cat in res:
            txt=txt+cat['category__name']+":"+int(cat['value'])/float(res_count)+"% "
    return txt

    
class Command(BaseCommand):
    polls=Poll.objects.order_by('-pk')
    res1=Menu.objects.get(slug='res1')
    res1.label="1"+polls[0].name
    res1.save()

    res2=Menu.objects.get(slug='res2')
    res2.label="2"+polls[1].name
    res2.save()

    res3=Menu.objects.get(slug='res3')
    res2.label="3"+polls[2].name
    res3.save()




    res11=Menu.objects.get(slug='res11')
    res11.label=get_results(polls[0])
    res11.save()
    res21=Menu.objects.get(slug='res21')
    res21.label=get_results(polls[1])
    res21.save()
    res31=Menu.objects.get(slug='res31')
    res31.label=get_results(polls[2])
    res31.save()

    def handle(self, **options):
        pass




