from django.conf.urls.defaults import *
from ureport.views import *

urlpatterns = patterns('',
    url(r'^ureport/$', tag_view,name="tag_view"),
    url(r'^ureport/polls/(?P<type>\w){0,1}/$', polls,{'template':'ureport/partials/all_polls.html'}),
    url(r'^ureport/polls/freeform/$', polls,{'template':'ureport/partials/freeform_polls.html','type':'t'}),
    url(r'^ureport/tag_cloud/$', tag_cloud),
    url(r'^ureport/messaging/$', messaging),
    url(r'^ureport/message_log/$', message_log),
    url(r'^ureport/pie_graph/$', pie_graph,name="pie_chart"),
    url(r'^ureport/histogram/$', histogram,name="histogram"),
    url(r'^ureport/map/$', map,name="map"),
    url(r'^ureport/dashboard/$', poll_dashboard,name="poll_dashboard"),
    url(r'^ureport/add_tag/$', add_drop_word),
    url(r'^ureport/delete_tag/$', delete_drop_word),
    url(r'^ureport/show_excluded/$', show_ignored_tags),
)