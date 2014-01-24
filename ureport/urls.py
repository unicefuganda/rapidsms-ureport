# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url, include
from ureport.views import poll_dashboard, ureporters, editReporter, deleteReporter, ureport_polls, script_polls, \
    messages, mass_messages, quit_messages, autoreg_messages, poll_messages, unsolicitized_messages, flagged_messages, \
    view_flagged_with, create_flags, delete_flag, view_responses, ureport_content, message_feed, poll_summary, \
    best_visualization, tag_cloud, add_drop_word, delete_drop_word, show_ignored_tags, histogram, show_timeseries, \
    get_all_contacts, bulk_upload_contacts, download_contacts_template, clickatell_wrapper, signup, ureporter_profile,\
    new_poll, mp_dashboard, ussd_manager, blacklist, delete, view_poll, poll_status, edit_category, delete_category, \
    delete_rule, view_rules, create_rule, alerts, remove_captured, send_message, view_autoreg_rules, set_autoreg_rules, \
    user_registration_status, kannel_status, a_dashboard, flag_categories, remove_captured_ind, assign_poll,\
    comfirm_message_sending, comfirmmessages, pulse, start_poll_export, cloud_dashboard, access_dashboards, map_cloud, extract_report
from django.contrib.auth.decorators import login_required
from generic.views import generic_row, generic
from contact.forms import FreeSearchForm, MultipleDistictFilterForm, GenderFilterForm, FilterGroupsForm, \
    AssignGroupForm, AgeFilterForm, MassTextForm
from tastypie.api import Api
from .api import PollResponseResource, PollResource, MessageResource, ContactResource, ResponseResource
from ureport.views.api.ViewUReporter import ViewUReporter
from ureport.views.api.currentpoll import ViewCurrentPoll
from ureport.views.excel_reports_views import generate_poll_dump_report, generate_per_district_report, upload_users, \
    assign_group
from rapidsms.models import Contact
from unregister.forms import BlacklistForm
from generic.sorters import SimpleSorter
from ureport.forms import AssignToNewPollForm
from ureport.models import Ureporter
from ureport.utils import get_contacts
from rapidsms.backends.vumi.views import VumiBackendView

message_resource = MessageResource()

v1_api = Api(api_name='v1')
v1_api.register(MessageResource())
v1_api.register(PollResponseResource())
v1_api.register(PollResource())
v1_api.register(ContactResource())
v1_api.register(ResponseResource())

urlpatterns = patterns('',
                       url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
                       # dashboard view for viewing all poll reports in one place
                       url(r'^dashboard/$', poll_dashboard, name="poll_dashboard"),

                       # ureporters (contact management views)
                       url(r'^reporter/$', ureporters, name="ureport-contact"),
                       url(r'^reporter/(?P<reporter_pk>\d+)/edit', editReporter, name="edit-reporter"),
                       url(r'^reporter/(?P<reporter_pk>\d+)/delete', deleteReporter, name="delete-reporter"),
                       url(r'^reporter/(?P<pk>\d+)/show', login_required(generic_row),
                           {'model': Contact, 'partial_row': 'ureport/partials/contacts/generic_contact_row.html'},
                           name="reporter-profile"),
                       # poll management views using generic (rather than built-in poll views
                       url(r'^mypolls/$', ureport_polls, name="ureport-polls", kwargs= {"pk": None}),
                       url(r'^mypolls/(?P<pk>\d+)/$', ureport_polls, name="ureport-polls"),

                       # poll management views using generic (rather than built-in poll views
                       url(r'^scriptpolls/$', script_polls, name="script-polls"),

                       url(r'^messages/$', messages, name="messagelog"),
                       url(r'^massmessages/$', mass_messages, name="massmessages"),
                       #Quit Messages View

                       url(r'^quitmessages/$', quit_messages, name="quitmessages"),
                       url(r'^autoreg_messages/$', autoreg_messages, name="autoreg_messages"),
                       url(r'^poll_messages/$', poll_messages, name="poll_messages"),
                       url(r'^unsolicitized_messages/$', unsolicitized_messages, name="unsolicitized_messages"),

                       #flagged messages
                       url(r'^flaggedmessages/$', login_required(flagged_messages), name="flaggedmessages"),

                       url(r"^flags/(?P<pk>\d+)/messages/$", view_flagged_with, name="flagged_with"),
                       url(r"^flags/new/$", create_flags, name="flags_new"),
                       url(r"^flags/(?P<pk>\d+)/edit/$", create_flags, name="flags_new"),
                       url(r'^flags/(?P<flag_pk>\d+)/delete/', delete_flag, name="delete_flag"),

                       # view responses for a poll (based on generic rather than built-in poll view
                       url(r"^(?P<poll_id>\d+)/responses/$", view_responses, name="responses"),

                       # content pages (cms-style static pages)
                       url(r'^content/(?P<slug>[a-z]+)/$', ureport_content, name="ureport_content"),
                       #url(r'^$', ureport_content, {'slug':'ureport_home', 'base_template':'ureport/three-square.html', 'num_columns':3}, name="rapidsms-dashboard"),
                       url(r'^home/$', ureport_content,
                           {'slug': 'ureport_home', 'base_template': 'ureport/three-square.html', 'num_columns': 3},
                           name="ureport-home"),
                       url(r'^about/$', ureport_content, {'slug': 'ureport_about'}, name="ureport-about"),
                       url(r'^stories/$', ureport_content,
                           {'slug': 'ureport_stories', 'base_template': 'ureport/three-square.html', 'num_columns': 3},
                           name="ureport-stories"),

                       # real-time message feed from the live poll
                       url(r'^messagefeed/$', message_feed, name="message-feed"),
                       url(r'^messagefeed/(?P<pks>\d+)/$', message_feed, name="message-feed"),

                       # polls page and best-visualization module (different viz based on poll type
                       url(r'^pollresults/$', poll_summary, name="polls-summary"), \
                       url(r'^bestviz/$', best_visualization, name="best-viz"),
                       url(r'^bestviz/(?P<poll_id>\d+)/$', best_visualization, name="best-viz"),

                       # tag cloud views
                       url(r'^tag_cloud/$', tag_cloud, name="tagcloud"),
                       url(r'^tag_cloud/(?P<pks>\d+)/$', tag_cloud, name="tag_cloud"),
                       url(r'^add_tag/$', add_drop_word, name="add_tag"),
                       url(r'^add_tag/(?P<tag_name>.+)/(?P<poll_pk>\d+)/$', add_drop_word, name="add_tag"),
                       url(r'^delete_tag/$', delete_drop_word, name="delete_tag"),
                       url(r'^delete_tag/(?P<tag_pk>\d+)/$', delete_drop_word, name="delete_tag"),
                       url(r'^show_excluded/$', show_ignored_tags, name="show_excluded"),
                       url(r'^show_excluded/(?P<poll_id>\d+)/$', show_ignored_tags, name="show_excluded"),

                       # histogram views
                       url(r'^histogram/$', histogram, name="histogram"),
                       url(r'^histogram/(?P<pks>\d+)/$', histogram, name="histogram"),

                       # total responses vs time view
                       url(r'^timeseries/$', show_timeseries, name="timeseries"),
                       url(r'^timeseries/(?P<pks>\d+)/$', show_timeseries, name="time-series"),

                       # export contacts to excel
                       url(r'^getcontacts/$', get_all_contacts, name="get_contacts"),
                       url(r'^uploadcontacts/$', bulk_upload_contacts, name="upload_contacts"),
                       #    url(r'^download/(?P<file>[a-z\.]+)/$', download_contacts_template),
                       url(r'^download/(?P<f>[a-z_\.]+)', download_contacts_template, name="download"),
                       # wrapper for clickatell api callbacks
                       url(r'^clickatell/$', clickatell_wrapper, name="clickatel"),
                       #    url(r'^ureport/maptest/', generic_map, {
                       #        'map_layers' : [{'name':'A poll','url':'/polls/responses/48/stats/1/'},
                       #                       ],
                       #    }),

                       url(r'^signup/$', signup, name="signup"),
                       url(r'^extract-report/$', extract_report, name="extract_report"),
                       url(r'^messagehistory/(?P<connection_pk>\d+)/$', ureporter_profile, name="profile"),
                       url(r'^createpoll/$', new_poll, name="new_poll"),
                       url(r'^mp_dashboard/$', mp_dashboard, name="mp_dashboard"),
                       url(r'^ussd_manager/$', ussd_manager, name="ussd_manager"),

                       url(r'^contact/(?P<pk>\d+)/blacklist/$', blacklist, name="blacklist"),
                       url(r'^contact/(?P<pk>\d+)/delete/$', delete, name="delete_contact"),
                       url(r'^view_poll/(?P<pk>\d+)/$', view_poll, name="view_poll"),
                       url(r'^poll_status/(?P<pk>\d+)/$', poll_status, name="poll_status"),
                       url(r'^category/(?P<pk>\d+)/edit/$', edit_category, name="edit_category"),
                       url(r'^category/(?P<pk>\d+)/delete/$', delete_category, name="delete_category"),
                       url(r'^rule/(?P<pk>\d+)/delete/$', delete_rule, name="delete_rule"),
                       url(r'^category/(?P<pk>\d+)/rules/view/$', view_rules, name="view_rules"),
                       url(r'^category/(?P<pk>\d+)/rules/create/$', create_rule, name="create_rule"),
                       url(r'^alerts/(?P<pk>\d+)/$', alerts, name="alerts"),
                       url(r"remove_captured/$", remove_captured, name="remove captured"),
                       url(r"sendmessage/$", send_message, name="send_message"),
                       url(r"view_group_rules/$", view_autoreg_rules, name="view_group_rules"),

                       url(r"set_group_rules/(?P<pk>\d+)/$", set_autoreg_rules, name="set_group_rules"),
                       url(r"set_group_rules/$", set_autoreg_rules, name="set_group_rules"),
                       url(r'^test_reg/(?P<connection>\d+)/$', user_registration_status,
                           name="user_registration_status"),
                       url(r"kannel_shaolin/$", kannel_status, name="kannel"),
                       (r'^accounts/password/reset/$', 'django.contrib.auth.views.password_reset',
                        {'post_reset_redirect': '/accounts/password/reset/done/'}),
                       (r'^accounts/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
                       (r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                        'django.contrib.auth.views.password_reset_confirm',
                        {'post_reset_redirect': '/accounts/password/done/'}),
                       (r'^accounts/password/done/$', 'django.contrib.auth.views.password_reset_complete'),
                       url(r'^dashboard/cloud/(?P<name>.*)/$', cloud_dashboard, name="cloud_dashboard"),
                       url(r'^dashboard/group/(?P<name>\w+)/$', flag_categories, name="flag-categories"),
                       url(r'^dashboard/(?P<name>\w+)/$', a_dashboard, name="aids-dashboard"),
                       url(r'^uncapture/(?P<pk>\d+)/$', remove_captured_ind, name="remove-captured_ind"),
                       url(r'^assign/(?P<pk>\d+)/(?P<poll>\d+)/$', assign_poll, name="remove-captured_ind"),
                       url(r'^reporter2/$', login_required(generic), {
                           'model': Ureporter,
                           'queryset': get_contacts,
                           'results_title': 'uReporters',
                           'filter_forms': [FreeSearchForm, GenderFilterForm, AgeFilterForm, MultipleDistictFilterForm,
                                            FilterGroupsForm],
                           'action_forms': [MassTextForm, AssignGroupForm, BlacklistForm, AssignToNewPollForm],
                           'objects_per_page': 25,
                           'partial_row': 'ureport/partials/contacts/contact_row2.html',
                           'base_template': 'ureport/ureporters_base.html',
                           'paginator_template': 'ureport/partials/pagination.html',
                           'columns': [('Age', False, '', None,),
                                       ('Gender', True, 'gender', SimpleSorter(),),
                                       ('Language', True, 'language', SimpleSorter(),),
                                       ('Location', True, 'reporting_location__name', SimpleSorter(),),
                                       ('Group(s)', True, 'groups__name', SimpleSorter()),
                                       ('Total Poll Responses', True, 'responses__count', SimpleSorter()),
                                       ('', False, '', None)],
                       }, name="ureport-contact2"),
                       (r'^api/', include(v1_api.urls)),
                       url(r'^comfirm/(?P<key>.+)/$', comfirm_message_sending, name="comfirm"),
                       url(r'^comfirmmessages/(?P<key>.+)/$', comfirmmessages, name="comfirm-messages"),
                       url(r"^dumpreport/(\d+)/$", generate_poll_dump_report),
                       url(r"^districtreport/(\d+)/$", generate_per_district_report),
                       url(r"^pulse/$", pulse, name='pulse_json'),
                       url(r"^pulse/(?P<period>\w+)/$", pulse, name='pulse_json'),
                       url(r"^map-cloud/$", map_cloud, name='map_cloud'),
                       url(r"^upload-contacts", upload_users, name='upload_users'),
                       url(r"^access/dashboards/$", access_dashboards, name='access_dashboards'),
                       url(r"^assign-group", assign_group, name="assign_group"),
                       url(r'^start_poll_export/(\d+)/$', start_poll_export, name="start_poll_export"),
                       url(r"^backend/vumi/$", VumiBackendView.as_view(backend_name="vumi")),
                       url(r"^ureporters/(?P<backend>\w+)/(?P<user_address>\w+)$", ViewUReporter.as_view()),
                       url(r"^ureporters/(?P<backend>\w+)/(?P<user_address>\w+)/polls/current$", ViewCurrentPoll.as_view()),

)
