# -*- coding: utf-8 -*-
from ussd.models import Menu
from poll.models import Poll


def get_results(poll):
    cats=[]
    response_count=poll.responses.count()
    if poll.categories.all().exists():
        for category in poll.categories.all():
            ccount=poll.responses.filter(categories__category=category).count()
            try:
                ccount_p=int(ccount*100/response_count)
            except ZeroDivisionError:
                return "0 responses"
            cats.append(str(category.name)+":"+str(ccount_p)+"%")
        return " ".join(cats)
    else:
        return str(response_count)+" responses"

def update_poll_results():
    latest_polls=Poll.objects.filter(categories__name__in=['yes','no']).distinct().order_by('-pk')
    res1=Menu.objects.get(slug="res1")

    res1.label=latest_polls[0].name
    res1.save()
    res2=Menu.objects.get(slug="res2")
    res2.label=latest_polls[1].name
    res2.save()
    res3=Menu.objects.get(slug="res3")
    res3.label=latest_polls[2].name
    res3.save()
    res11=Menu.objects.get(slug="res11")
    res11.label=get_results(latest_polls[0])
    res11.save()
    res21=Menu.objects.get(slug="res21")
    res21.label=get_results(latest_polls[1])
    res21.save()

    res31=Menu.objects.get(slug="res31")
    res31.label=get_results(latest_polls[2])
    res31.save()
