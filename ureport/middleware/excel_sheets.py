from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.http import HttpResponseRedirect
import re
from django.contrib.auth.decorators import user_passes_test
from ureport.models import Permit

class RequirePermissionMiddleware(object):

    def __init__(self):
        self.allowed = tuple([re.compile(url) for url in settings.ALLOWED])

    def process_view(self,request,view_func,view_args,view_kwargs):

        if not request.user.is_staff and request.user.is_authenticated():
           import pdb;pdb.set_trace()

