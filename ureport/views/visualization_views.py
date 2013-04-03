#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404
from ureport.models import IgnoredTags
from django.contrib.auth.decorators import login_required
from ureport.utils import retrieve_poll
from django.views.decorators.cache import cache_control
from poll.models import Poll
import bisect
import textwrap
import datetime
from eav.models import Value

from poll.models import ResponseCategory, Response
from ureport.views.utils.tags import _get_tags, _get_responses
from django.db import transaction


@transaction.autocommit
def best_visualization(request, poll_id=None):
    module = False
    if 'module' in request.GET:
        module = True
    polls = retrieve_poll(request, poll_id)
    try:
        poll = polls[0]
    except IndexError:
        raise Http404

    #    if poll_id:
    #        poll = Poll.objects.get(pk=poll_id)
    #    else:
    #        poll = Poll.objects.latest('start_date')
    try:
        rate = poll.responses.count() * 100 / poll.contacts.count()
    except ZeroDivisionError:
        rate = 0

    dict_to_render = {
        'poll': poll,
        'polls': [poll],
        'unlabeled': True,
        'module': module,
        'rate': int(rate),
        }
    if poll.type == Poll.TYPE_TEXT and not  poll.categories.exists():
        dict_to_render.update({'tags': _get_tags(polls),
                    'responses': _get_responses(poll),
                    'poll_id': poll.pk})
    return render_to_response('ureport/partials/viz/best_visualization.html'
                              , dict_to_render,
                              context_instance=RequestContext(request))


@login_required
def add_drop_word(request, tag_name=None, poll_pk=None):
    IgnoredTags.objects.create(name=tag_name,
                               poll=get_object_or_404(Poll,
                               pk=int(poll_pk)))
    return HttpResponse(simplejson.dumps('success'))


@login_required
def delete_drop_word(request, tag_pk):
    tag = get_object_or_404(IgnoredTags, pk=int(tag_pk))
    tag.delete()
    return HttpResponse(simplejson.dumps('success'))


@login_required
@cache_control(no_cache=True, max_age=0)
def show_ignored_tags(request, poll_id):
    tags = IgnoredTags.objects.filter(poll__pk=poll_id)
    return render_to_response('ureport/partials/tag_cloud/ignored_tags.html'
                              , {'tags': tags, 'poll_id': poll_id},
                              context_instance=RequestContext(request))


@cache_control(no_cache=True, max_age=0)
@transaction.autocommit
def tag_cloud(request, pks):
    """
        generates a tag cloud
    """

    polls = retrieve_poll(request, pks)

    poll_qn = ['Qn:' + ' '.join(textwrap.wrap(poll.question.rsplit('?'
               )[0])) + '?' for poll in polls]

    tags = _get_tags(polls)
    return render_to_response('ureport/partials/tag_cloud/tag_cloud.html'
                              , {
        'poll': polls[0],
        'tags': tags,
        'poll_qn': poll_qn[0],
        'poll_id': pks,
        }, context_instance=RequestContext(request))

@transaction.autocommit
def histogram(request, pks=None):
    """
         view for numeric polls
    """

    all_polls = Poll.objects.filter(type=u'n')
    pks = (pks if pks != None else request.GET.get('pks', None))
    if pks:
        items = 6
        polls = retrieve_poll(request, pks)
        responses = Response.objects.filter(poll__in=polls)
        pks = polls.values_list('pk', flat=True)
        responses = Response.objects.filter(poll__in=polls,
                poll__type=u'n')
        plottable_data = {}
        if responses:
            poll_results = {}
            poll_qns = ['Qn:' + poll.question + '<br>' for poll in
                        Poll.objects.filter(pk__in=pks)]

            total_responses = responses.count()
            vals_list = \
                Value.objects.filter(entity_id__in=responses).values_list('value_float'
                    , flat=True)
            vals_list = sorted(vals_list)
            max = int(vals_list[-1])
            min = int(vals_list[0])
            num_list = range(min, max)
            increment = int(max / items)
            bounds = num_list[::increment]
            ranges_list = [str(a) + '-' + str(a + increment) for a in
                           bounds if a < max]
            poll_results['categories'] = ranges_list
            poll_results['title'] = poll_qns

            for response in responses:
                name = response.poll.name
                poll_results.setdefault(name, {})
                poll_results[name].setdefault('data', {})
                if len(response.eav_values.all()) > 0:
                    value = \
                        int(response.eav_values.all()[0].value_float)
                pos = bisect.bisect_right(bounds, value) - 1
                r = ranges_list[pos]
                poll_results[name]['data'].setdefault(r, 0)
                poll_results[name]['data'][r] += 1

            data = []
            for key in poll_results.keys():
                if key not in ['categories', 'title']:
                    d = {}
                    d['name'] = key
                    d['data'] = poll_results[key]['data'].values()
                    data.append(d)
            plottable_data['data'] = data
            plottable_data['title'] = poll_qns
            plottable_data['categories'] = ranges_list
            plottable_data['mean'] = sum(vals_list) / len(vals_list)
            plottable_data['median'] = vals_list[len(vals_list) / 2]
        return HttpResponse(mark_safe(simplejson.dumps(plottable_data)))

    return render_to_response('ureport/partials/viz/histogram.html',
                              {'polls': all_polls},
                              context_instance=RequestContext(request))

@transaction.autocommit
def show_timeseries(request, pks):
    polls = retrieve_poll(request, pks)
    poll_obj = polls[0]
    responses = Response.objects.filter(poll=poll_obj)
    start_date = poll_obj.start_date
    end_date = poll_obj.end_date or datetime.datetime.now()
    poll = poll_obj.question.replace('"', '\\"')
    interval = datetime.timedelta(minutes=60)
    current_date = start_date
    message_count_list = []
    while current_date < end_date:
        count = responses.filter(message__date__range=(start_date,
                                 current_date)).count()
        message_count_list.append(count)
        current_date += interval

    return render_to_response('ureport/partials/viz/timeseries.html', {
        'counts': mark_safe(message_count_list),
        'start': start_date,
        'end': end_date,
        'poll': mark_safe(poll),
        }, context_instance=RequestContext(request))


