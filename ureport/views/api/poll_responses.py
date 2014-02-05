from django.http import HttpResponseBadRequest
from simplejson import JSONDecodeError
from rapidsms.messages import IncomingMessage
from rapidsms_httprouter.models import Message
from script.models import ScriptProgress, ScriptSession, ScriptResponse
from ureport.views.api.base import UReporterApiView, UReportPostApiViewMixin


class SubmitPollResponses(UReportPostApiViewMixin, UReporterApiView):
    def create_incoming_message(self, incoming_response):
        incoming_message = IncomingMessage(self.connection, incoming_response)
        incoming_message.db_message = Message.objects.create(direction='I', connection=self.connection,
                                                             text=incoming_response)
        return incoming_message

    def get_incoming_response(self, request):
        incoming_json_data = self.get_json_data(request)
        incoming_response = incoming_json_data["response"]
        return incoming_response

    def create_script_response(self, response):
        ss = ScriptSession.objects.get(connection=self.connection)
        ScriptResponse.objects.create(session=ss, response=response)

    def process_poll_response(self, incoming_response_text, poll):
        incoming_message = self.create_incoming_message(incoming_response_text)
        response, outgoing_message = poll.process_response(incoming_message)
        self.create_script_response(response)
        return (not response.has_errors), outgoing_message

    def post(self, request, *args, **kwargs):
        poll_id = kwargs.get("poll_id")
        poll = self.get_poll(poll_id)
        try:
            incoming_response = self.get_incoming_response(request)
        except (JSONDecodeError, KeyError):
            return HttpResponseBadRequest("Incoming response was in a wrong format.")
        accepted, outgoing_message = self.process_poll_response(incoming_response, poll)
        if accepted:
            self.process_registration_steps(poll)
        json_response_data = {"success": True, "result": {"accepted": accepted, "response": outgoing_message}}
        return self.create_json_response(json_response_data)

    def process_registration_steps(self, poll):
        script_progress = self.get_script_progress_for_poll(poll)
        if script_progress:
            script_progress.moveon()

    def get_script_progress_for_poll(self, fake_poll):
        script_progress = None
        try:
            script_progress = ScriptProgress.objects.get(connection=self.connection, step__poll=fake_poll)
        except ScriptProgress.DoesNotExist:
            pass
        return script_progress