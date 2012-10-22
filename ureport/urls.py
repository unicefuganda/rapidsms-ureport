# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ureport.views import *
from django.contrib.auth.decorators import login_required
from generic.views import  generic_row


urlpatterns = patterns('',
    # dashboard view for viewing all poll reports in one place
    url(r'^dashboard/$',poll_dashboard, name="poll_dashboard"),

    # ureporters (contact management views)
    url(r'^reporter/$', ureporters, name="ureport-contact"),
    url(r'^reporter/(?P<reporter_pk>\d+)/edit', editReporter,name="edit-reporter"),
    url(r'^reporter/(?P<reporter_pk>\d+)/delete', deleteReporter,name="delete-reporter"),
    url(r'^reporter/(?P<pk>\d+)/show', login_required(generic_row), {'model':Contact, 'partial_row':'ureport/partials/contacts/contacts_row.html'},name="reporter-profile"),
    # poll management views using generic (rather than built-in poll views
    url(r'^mypolls/$', ureport_polls, name="ureport-polls"),

    # poll management views using generic (rather than built-in poll views
    url(r'^scriptpolls/$', script_polls, name="script-polls"),

     url(r'^messages/$', messages, name="messagelog"),
     url(r'^massmessages/$',mass_messages,name="massmessages"),
    #Quit Messages View

    url(r'^quitmessages/$', quit_messages,name="quitmessages"),
    url(r'^autoreg_messages/$', autoreg_messages,name="autoreg_messages"),
    url(r'^poll_messages/$', poll_messages,name="poll_messages"),
    url(r'^unsolicitized_messages/$', unsolicitized_messages,name="unsolicitized_messages"),

    #flagged messages
    url(r'^flaggedmessages/$', login_required(flagged_messages),name="flaggedmessages"),

    url(r"^flags/(?P<pk>\d+)/messages/$", view_flagged_with, name="flagged_with"),
     url(r"^flags/new/$", create_flags , name="flags_new"),
     url(r"^flags/(?P<pk>\d+)/edit/$", create_flags , name="flags_new"),
     url(r'^flags/(?P<flag_pk>\d+)/delete/', delete_flag, name="delete_flag"),

    # view responses for a poll (based on generic rather than built-in poll view
    url(r"^(?P<poll_id>\d+)/responses/$", view_responses, name="responses"),

    # content pages (cms-style static pages)
    url(r'^content/(?P<slug>[a-z]+)/$', ureport_content,name="ureport_content"),
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
    url(r'^getcontacts/$', get_all_contacts,name="get_contacts"),
    url(r'^uploadcontacts/$', bulk_upload_contacts,name="upload_contacts"),
#    url(r'^download/(?P<file>[a-z\.]+)/$', download_contacts_template),
    url(r'^download/(?P<f>[a-z_\.]+)', download_contacts_template,name="download"),
    # wrapper for clickatell api callbacks
    url(r'^clickatell/$', clickatell_wrapper,name="clickatel"),
#    url(r'^ureport/maptest/', generic_map, {
#        'map_layers' : [{'name':'A poll','url':'/polls/responses/48/stats/1/'},
#                       ],
#    }),

    url(r'signup/$',signup,name="signup"),
    url(r'messagehistory/(?P<connection_pk>\d+)/$',ureporter_profile,name="profile"),
     url(r'createpoll/$',new_poll,name="new_poll"),
     url(r'mp_dashboard/$',mp_dashboard,name="mp_dashboard"),
       url(r'ussd_manager/$',ussd_manager,name="ussd_manager"),

       url(r'^contact/(?P<pk>\d+)/blacklist/$', blacklist, name="blacklist"),
       url(r'^contact/(?P<pk>\d+)/delete/$', delete, name="delete_contact"),
        url(r'^view_poll/(?P<pk>\d+)/$', view_poll, name="view_poll"),
    url(r'^category/(?P<pk>\d+)/edit/$', edit_category, name="edit_category"),
    url(r'^category/(?P<pk>\d+)/delete/$', delete_category, name="delete_category"),
    url(r'^category/(?P<pk>\d+)/rules/view/$', view_rules, name="view_rules"),
    url(r'^category/(?P<pk>\d+)/rules/create/$', create_rule, name="create_rule"),
    url(r'^alerts/$', alerts, name="alerts"),
    url(r"remove_captured/$",remove_captured,name="remove captured"),
    url(r"sendmessage/$",send_message,name="send_message"),
    url(r"group_rules/$",set_autoreg_rules,name="set_group_rules"),
    url(r"kannel_shaolin/$",kannel_status,name="kannel"),
    (r'^accounts/password/reset/$', 'django.contrib.auth.views.password_reset',
         {'post_reset_redirect' : '/accounts/password/reset/done/'}),
    (r'^accounts/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',
         {'post_reset_redirect' : '/accounts/password/done/'}),
    (r'^accounts/password/done/$', 'django.contrib.auth.views.password_reset_complete'),
    url(r'^aids_dashboard/$', aids_dashboard, name="aids-dashboard"),
)
