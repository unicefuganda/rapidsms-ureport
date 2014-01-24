from django.http import HttpResponse
from ureport.views.api.base import UReporterApiView
from django.utils import simplejson as json


class ViewPollResponses(UReporterApiView):
    def post(self, request, *args, **kwargs):
        return HttpResponse(status=200)

    def get(self, request, *args, **kwargs):
        return HttpResponse("Method Not Allowed", status=405)

    def get_json_data(self, request):
        #TODO: This only works for Django 1.3, it would need to be changed in case of an upgrade
        try:
            json_content = request.body
        except AttributeError:
            json_content = request.POST.items()[0][0]
        return json.loads(json_content)