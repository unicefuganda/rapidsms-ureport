from django.conf.urls.defaults import *
from ureport.views import *

urlpatterns = patterns('',
   url(r'^ureport/$', tag_view,name="tag_view"),
   url(r'^ureport/polls/$', freeform_polls),
   url(r'^ureport/tag_cloud/$', tag_cloud),
   url(r'^ureport/messaging/$', messaging),
   url(r'^ureport/send_message/$', send_message)
)