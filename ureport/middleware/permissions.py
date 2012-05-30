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

        if not request.user.is_staff and request.user.is_authenticated() and request.user.has_perm('rapidsms.restricted_access'):
            #import pdb;pdb.set_trace()
            try:
                permit=Permit.objects.filter(user=request.user).order_by('-date')
                paths=permit[0].get_patterns()

                for path in paths:
                    if path and path.match(request.path)  :
                        return None
            except:
                pass
            for p in self.allowed:
                if p.match(request.path):
                    return None

            return HttpResponseRedirect("/")
        else:
            return None

