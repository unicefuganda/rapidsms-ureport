from django.conf.urls.defaults import *
from ureport.views import *
from ureport.utils import get_contacts, get_polls
from django.contrib.auth.decorators import login_required
from contact.forms import FreeSearchForm, DistictFilterForm, FilterGroupsForm, AssignGroupForm, MassTextForm
from generic.views import generic, generic_row
from generic.sorters import SimpleSorter
from unregister.forms import BlacklistForm

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
    url(r'^ureport/dashboard/$', login_required(generic), {
        'model':Poll,
        'queryset':get_polls,
        'filter_forms':[],
        'action_forms':[],
        'objects_per_page':10,
        'partial_row':'ureport/partials/poll_row.html',
        'partial_header':'ureport/partials/partial_header_dashboard.html',
        'base_template':'ureport/dashboard.html',
        'selectable':False,
        'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Question', True, 'question', SimpleSorter(),),
                 ('Start Date',True,'start_date', SimpleSorter(),),
                 ('# Participants', False, 'participants',None,),
                 ('Visuals',False,'visuals',None,),
                 ],
        'sort_column':'start_date',
        'sort_ascending':False,
    }, name="poll_dashboard"),
    url(r'^ureport/add_tag/$', login_required(add_drop_word)),
    url(r'^ureport/delete_tag/$', login_required(delete_drop_word)),
    url(r'^ureport/show_excluded/$', login_required(show_ignored_tags)),
    url(r"^ureport/(\d+)/message_history/$", login_required(view_message_history)),
    url(r'^ureport/timeseries/(?P<poll>\d+)/$',show_timeseries),
    url(r'^ureport/reporter/$', login_required(generic), {
        'model':Contact,
        'queryset':get_contacts,
        'filter_forms':[FreeSearchForm, DistictFilterForm, FilterGroupsForm],
        'action_forms':[MassTextForm, AssignGroupForm, BlacklistForm],
        'objects_per_page':25,
        'partial_row':'ureport/partials/contacts_row.html',
        'base_template':'ureport/contacts_base.html',
        'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Number', True, 'connection__identity', SimpleSorter(),),
                 ('Location',True,'reporting_location__name', SimpleSorter(),),
                 ('Group(s)', True, 'groups__name',SimpleSorter()),
                 ('Total Poll Responses',True,'responses__count',SimpleSorter()),
                 ('',False,'',None)],
    }, name="ureport-contact"),
    url(r'^ureport/reporter/(?P<reporter_pk>\d+)/edit', editReporter),
    url(r'^ureport/reporter/(?P<reporter_pk>\d+)/delete', deleteReporter),
    url(r'^ureport/reporter/(?P<pk>\d+)/show', generic_row, {'model':Contact, 'partial_row':'ureport/partials/contacts_row.html'}),
)