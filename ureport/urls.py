from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from ureport.views import *
from ureport.utils import get_contacts, get_polls
from django.contrib.auth.decorators import login_required
from contact.forms import FreeSearchForm,GenderFilterForm, DistictFilterForm, FilterGroupsForm, AssignGroupForm, MassTextForm, AgeFilterForm
from generic.views import generic, generic_row, generic_dashboard, generic_map
from generic.sorters import SimpleSorter
from unregister.forms import BlacklistForm
from poll.models import *

urlpatterns = patterns('',
    # dashboard view for viewing all poll reports in one place
    url(r'^dashboard/$', generic, {
        'model':Poll,
        'queryset':get_polls,
        'results_title':'Polls',
        'filter_forms':[],
        'action_forms':[],
        'objects_per_page':10,
        'partial_row':'ureport/partials/dashboard/poll_row.html',
        'partial_header':'ureport/partials/dashboard/partial_header_dashboard.html',
        'base_template':'ureport/dashboard.html',
        'selectable':False,
        'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Question', True, 'question', SimpleSorter(),),
                 ('Start Date', True, 'start_date', SimpleSorter(),),
                 ('# Participants', False, 'participants', None,),
                 ('Visuals', False, 'visuals', None,),
                 ],
        'sort_column':'start_date',
        'sort_ascending':False,
    }, name="poll_dashboard"),

    # ureporters (contact management views)
    url(r'^reporter/$', login_required(generic), {
        'model':Contact,
        'queryset':get_contacts,
        'results_title':'uReporters',
        'filter_forms':[ FreeSearchForm, DistictFilterForm, FilterGroupsForm,GenderFilterForm,AgeFilterForm],
        'action_forms':[MassTextForm, AssignGroupForm, BlacklistForm],
        'objects_per_page':25,
        'partial_row':'ureport/partials/contacts/contacts_row.html',
        'base_template':'ureport/contacts_base.html',
        'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Number', True, 'connection__identity', SimpleSorter(),),
                 ('Location', True, 'reporting_location__name', SimpleSorter(),),
                 ('Group(s)', True, 'groups__name', SimpleSorter()),
                 ('Total Poll Responses', True, 'responses__count', SimpleSorter()),
                 ('', False, '', None)],
    }, name="ureport-contact"),
    url(r'^reporter/(?P<reporter_pk>\d+)/edit', editReporter),
    url(r'^reporter/(?P<reporter_pk>\d+)/delete', deleteReporter),
    url(r'^reporter/(?P<pk>\d+)/show', generic_row, {'model':Contact, 'partial_row':'ureport/partials/contacts/contacts_row.html'}),

    # poll management views using generic (rather than built-in poll views
    url(r'^mypolls/$', generic, {
        'model':Poll,
        'queryset':get_polls,
        'objects_per_page':10,
        'selectable':False,
        'partial_row':'ureport/partials/polls/poll_admin_row.html',
        'base_template':'ureport/poll_admin_base.html',
        'results_title':'Polls',
        'sort_column':'start_date',
        'sort_ascending':False,
        'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Question', True, 'question', SimpleSorter(),),
                 ('Start Date', True, 'start_date', SimpleSorter(),),
                 ('Closing Date', True, 'end_date', SimpleSorter()),
                 ('', False, '', None)],
    }, name="ureport-polls"),

    # view responses for a poll (based on generic rather than built-in poll view
    url(r"^(\d+)/responses/$", view_responses, name="responses"),

    # content pages (cms-style static pages)
    url(r'^content/(?P<slug>[a-z]+)/$', ureport_content),
    #url(r'^$', ureport_content, {'slug':'ureport_home', 'base_template':'ureport/three-square.html', 'num_columns':3}, name="rapidsms-dashboard"),
    url(r'^home/$', ureport_content, {'slug':'ureport_home', 'base_template':'ureport/three-square.html', 'num_columns':3}, name="ureport-home"),
    url(r'^about/$', ureport_content, {'slug':'ureport_about'}, name="ureport-about"),
    url(r'^stories/$', ureport_content, {'slug':'ureport_stories', 'base_template':'ureport/three-square.html', 'num_columns':3}, name="ureport-stories"),

    # real-time message feed from the live poll
    url(r'^messagefeed/$', message_feed, name="message-feed"),
    url(r'^messagefeed/(?P<pks>\d+)/$', message_feed, name="message-feed"),

    # polls page and best-visualization module (different viz based on poll type
    url(r'^pollresults/$', poll_summary, name="polls-summary"), \
    url(r'^bestviz/$', best_visualization, name="best-viz"),
    url(r'^bestviz/(?P<poll_id>\d+)/$', best_visualization, name="best-viz"),

    # tag cloud views
    url(r'^tag_cloud/$', tag_cloud, name="tag_cloud"),
    url(r'^tag_cloud/(?P<pks>\d+)/$', tag_cloud, name="tag_cloud"),
    url(r'^add_tag/$', add_drop_word, name="add_tag"),
    url(r'^add_tag/(?P<tag_name>[a-zA-Z]+)/(?P<poll_pk>\d+)/$', add_drop_word, name="add_tag"),
    url(r'^delete_tag/$', delete_drop_word, name="delete_tag"),
    url(r'^delete_tag/(?P<tag_pk>\d+)/$', delete_drop_word, name="delete_tag"),
    url(r'^show_excluded/$', show_ignored_tags, name="show_excluded"),
    url(r'^show_excluded/(?P<poll_id>\d+)/$', show_ignored_tags, name="show_excluded"),

    # histogram views
    url(r'^histogram/$', histogram, name="histogram"),
    url(r'^histogram/(?P<pks>\d+)/$', histogram, name="histogram"),

    # total responses vs time view
    url(r'^timeseries/$', show_timeseries, name="time-series"),
    url(r'^timeseries/(?P<pks>\d+)/$', show_timeseries, name="time-series"),

    # export contacts to excel
    url(r'^getcontacts/$', get_all_contacts),
    url(r'^uploadcontacts/$', bulk_upload_contacts),
#    url(r'^download/(?P<file>[a-z\.]+)/$', download_contacts_template),
    url(r'^download/(?P<f>[a-z_\.]+)', download_contacts_template),
    # wrapper for clickatell api callbacks
    url(r'^clickatell/$', clickatell_wrapper),
#    url(r'^ureport/maptest/', generic_map, { 
#        'map_layers' : [{'name':'A poll','url':'/polls/responses/48/stats/1/'},
#                       ],
#    }),
)
