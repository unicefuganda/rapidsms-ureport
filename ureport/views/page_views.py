#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib2
from django.shortcuts import  get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from generic.views import  generic_dashboard
from generic.forms import StaticModuleForm
from generic.models import Dashboard
from ureport.forms import PollModuleForm


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
    resp, content = conn.request('http://ureport.ug:13000/status', request.method)
    return HttpResponse(content,content_type="text/html")

