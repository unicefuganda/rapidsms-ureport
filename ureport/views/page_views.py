#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache

import httplib2
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from generic.views import generic_dashboard
from generic.forms import StaticModuleForm
from generic.models import Dashboard
from ureport.forms import PollModuleForm
from message_classifier.models import IbmCategory, IbmMsgCategory
from rapidsms.contrib.locations.models import Location


def ureport_content(
        request,
        slug,
        base_template='ureport/two-column.html',
        **kwargs
):
    createpage = kwargs.setdefault('create', False)
    if not createpage:
        reporter = get_object_or_404(Dashboard, slug=slug, user=None)
    return generic_dashboard(
        request,
        slug=slug,
        module_types=[('ureport', PollModuleForm,
                       'uReport Visualizations'), ('static',
                                                   StaticModuleForm, 'Static Content')],
        base_template=base_template,
        title=None,
        **kwargs
    )


@login_required
def kannel_status(request):
    conn = httplib2.Http()
    (resp, content) = conn.request('http://ureport.ug:13000/status',
                                   request.method)
    return HttpResponse(content, content_type='text/html')


def pulse(request, period=None):
    period_map = {'day': 1, 'month': 30, 'year': 365}
    l = [l.pk for l in Location.objects.filter(type='district').distinct()]

    if period:
        print period, "is here now"
        now = datetime.datetime.now()
        previous_date = datetime.datetime.now() - datetime.timedelta(days=period_map[period])
        _all = IbmMsgCategory.objects.filter(score__gte=0.5,
                                             msg__connection__contact__reporting_location__in=l).values_list('pk', flat=True)
        s = IbmCategory.objects.filter(ibmmsgcategory__in=_all).exclude(
            name__in=['family & relationships', "energy", "u-report", "social policy", "employment"]).annotate(
            total=Count('ibmmsgcategory')).values('name', 'total',
                                                       'ibmmsgcategory__msg__connection__contact__reporting_location__name')
        print s.query
    else:
        s = IbmCategory.objects.filter(ibmmsgcategory__score__gte=0.5,
                                       ibmmsgcategory__msg__connection__contact__reporting_location__in=l).annotate(
            total=Count('ibmmsgcategory')).values('total', 'name',
                                                  'ibmmsgcategory__msg__connection__contact__reporting_location__name'). \
            exclude(name__in=['family & relationships', "energy", "u-report", "social policy", "employment"])
        print s.query
    data = json.dumps(list(s), cls=DjangoJSONEncoder)
    return HttpResponse(data.replace('"ibmmsgcategory__msg__connection__contact__reporting_location__name"',
                                     "\"district\"").replace("\"name\"", "\"category\""),
                        content_type='application/json')


def national_pulse(request, period=None):
    print period
    return render_to_response('ureport/national_pulse.html', locals(), context_instance=RequestContext(request))