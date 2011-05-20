"""A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.
"""
from django.conf import settings
from ureport.settings import MAP_URLS, MAP_TYPES, min_lat, max_lat, min_lon, max_lon, colors
from django.utils.safestring import mark_safe
from django.utils import simplejson

def map_params(request):
    """
    a context processor that passes all the pertinent map parameters to all templates.
    """
    map_keys = getattr(settings, 'MAP_KEY', '')
    if type(map_keys) == list:
        map_key = map_keys[0][1]
        for domain, key in map_keys:
            if request.get_host() == domain:
                map_key = key
    else:
        map_key = map_keys
    print "MAP KEY IS %s" % map_key
    return {
        'map_key':map_key,
        'colors':colors,
        'min_lat':min_lat,
        'max_lat':max_lat,
        'min_lon':min_lon,
        'max_lon':max_lon,
        'map_urls':mark_safe(simplejson.dumps(MAP_URLS)),
        'map_types':mark_safe(simplejson.dumps(MAP_TYPES)),        
    }

