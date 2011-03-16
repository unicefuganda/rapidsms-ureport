"""A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.
"""
from django.conf import settings
from ureport.settings import MAP_URLS, MAP_TYPES, min_lat, max_lat, min_lon, max_lon
from django.utils.safestring import mark_safe
from django.utils import simplejson

def map_params(request):
    """
    a context processor that passes all the pertinent map parameters to all templates.
    """
    return {
        'map_key':settings.MAP_KEY,
        'colors':['#4572A7', '#AA4643', '#89A54E', '#80699B', '#3D96AE', '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92'],
        'minLat':min_lon,
        'maxLat':max_lon,
        'minLon':min_lat,
        'maxLon':max_lat,
        'Map_urls':mark_safe(simplejson.dumps(MAP_URLS)),
        'map_types':mark_safe(simplejson.dumps(MAP_TYPES)),        
    }

