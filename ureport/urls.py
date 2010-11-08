from django.conf.urls.defaults import *
from ureport.views import *

urlpatterns = patterns('',
   url(r'^ureport/$', tag_view,name="tag_view"),
   url(r'^ureport/polls/(?P<type>\w){0,1}/$', polls,{'template':'ureport/partials/all_polls.html'}),
   url(r'^ureport/tag_cloud/$', tag_cloud),
   url(r'^ureport/messaging/$', messaging),
   url(r'^ureport/pie_graph/$', pie_graph,name="pie_chart"),
   url(r'^ureport/histogram/$',  histogram,name="histogram"),
    url(r'^ureport/map/$',  map,name="map"),
)