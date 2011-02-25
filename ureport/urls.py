from django.conf.urls.defaults import *
from ureport.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^ureport/$', login_required(tag_view),name="tag_view"),
    url(r'^ureport/polls/(?P<type>\w){0,1}/$', login_required(polls),{'template':'ureport/partials/all_polls.html'}),
    url(r'^ureport/polls/freeform/$', login_required(polls),{'template':'ureport/partials/freeform_polls.html','type':'t'}),
    url(r'^ureport/tag_cloud/$', login_required(tag_cloud)),
    url(r'^ureport/messaging/$', login_required(messaging), name='ureport-messaging'),
    url(r'^ureport/message_log/$', login_required(message_log), name='ureport-messagelog'),
    url(r'^ureport/pie_graph/$', login_required(pie_graph),name="pie_chart"),
    url(r'^ureport/histogram/$', login_required(histogram),name="histogram"),
    url(r'^ureport/map/$', login_required(map),name="map"),
    url(r'^ureport/dashboard/$', login_required(poll_dashboard),name="poll_dashboard"),
    url(r'^ureport/add_tag/$', login_required(add_drop_word)),
    url(r'^ureport/delete_tag/$', login_required(delete_drop_word)),
    url(r'^ureport/show_excluded/$', login_required(show_ignored_tags)),
    url(r"^ureport/(\d+)/message_history/$", login_required(view_message_history)),
    url(r'^ureport/timeseries/(?P<poll>\d+)/$',show_timeseries),
)