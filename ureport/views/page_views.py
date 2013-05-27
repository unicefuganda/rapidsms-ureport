#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.db.models import Count
from django.views.decorators.cache import never_cache

import httplib2
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from generic.views import generic_dashboard
from generic.forms import StaticModuleForm
from generic.models import Dashboard
from ureport.forms import PollModuleForm
from message_classifier.models import IbmCategory
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


@never_cache
def national_pulse(request):
    l = [l.pk for l in Location.objects.filter(type='district').distinct()]

    s = IbmCategory.objects.filter(ibmmsgcategory__score__gte=0.25,
                                   ibmmsgcategory__msg__connection__contact__reporting_location__in=l).annotate(
        total=Count('ibmmsgcategory')).values('total', 'name',
                                              'ibmmsgcategory__msg__connection__contact__reporting_location__name'). \
        exclude(name__in=['family & relationships', "energy", "u-report", "social policy", "employment"])

    data = json.dumps(list(s))
    return HttpResponse(data.replace('"ibmmsgcategory__msg__connection__contact__reporting_location__name"',
                                     "\"district\"").replace("\"name\"", "\"category\""),
                        content_type='application/json')