#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.template import loader
try:
    from django.conf.settings import DEBUG
except AttributeError:
    DEBUG =False


template_cache = {}
original_get_template = loader.get_template
def cached_get_template(template_name):
    global template_cache
    t = template_cache.get(template_name,None)
    if not t or DEBUG:
        template_cache[template_name] = t = original_get_template(template_name)
    return t
loader.get_template = cached_get_template
