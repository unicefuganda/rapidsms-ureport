from django.http import Http404, HttpResponseBadRequest
from simplejson import JSONDecodeError
from rapidsms_httprouter.router import get_router
from ureport.views.api.base import UReporterApiView, UReportPostApiViewMixin
from rapidsms_httprouter.tasks import handle_incoming


class SubmitReportApiView(UReportPostApiViewMixin, UReporterApiView):
    def post(self, request, *args, **kwargs):
        if not self.contact_exists(self.connection):
            raise Http404
        try:
            incoming_report_text = self.get_incoming_report(request)
            self.process_report(incoming_report_text)
        except (JSONDecodeError, KeyError):
            return HttpResponseBadRequest("Incoming response was in a wrong format.")

        return self.create_json_response({"success": True, "response": "Thank you for your report"})

    def get_incoming_report(self, request):
        incoming_json_data = self.get_json_data(request)
        incoming_response = incoming_json_data["report"]
        return incoming_response

    def process_report(self, message):
        handle_incoming.delay(get_router(), self.backend, self.user_address, message)