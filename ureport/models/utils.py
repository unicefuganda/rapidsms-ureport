# -*- coding: utf-8 -*-
from rapidsms_httprouter.models import Message, STATUS_CHOICES
from ussd.models import Menu
from poll.models import Poll
import datetime


def get_results(poll):
    cats=[]
    response_count=poll.responses.count()
    if poll.categories.all():
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
    res11=Menu.objects.get(slug="res11")
    res11.label=get_results(latest_polls[0])
    res11.save()
    try:
        #We don't know that there is going to be more than one poll in ureport
        #Todo Get a better way to do all this
        res2=Menu.objects.get(slug="res2")
        res2.label=latest_polls[1].name
        res2.save()
        res3=Menu.objects.get(slug="res3")
        res3.label=latest_polls[2].name
        res3.save()
        res21=Menu.objects.get(slug="res21")
        res21.label=get_results(latest_polls[1])
        res21.save()

        res31=Menu.objects.get(slug="res31")
        res31.label=get_results(latest_polls[2])
        res31.save()
    except IndexError:
        pass

def recent_message_stats(poll, start_date, since_days_ago):
    query_date = start_date - datetime.timedelta(days=since_days_ago)

    stats = {}

    stats['Total'] = len(poll.messages.all())
    for status in STATUS_CHOICES:
        code=status[0]
        name=status[1]
        stats[name] = poll.messages.filter(date__gt=query_date, direction='O', status=code).count()

    return stats