from django.http import HttpResponseNotAllowed, Http404
from ureport.views.api.base import UReporterApiView


class PollTopicsApiView(UReporterApiView):
    def post(self, request, *args, **kwargs):
        return HttpResponseNotAllowed("Method Not Allowed")

    def get(self, request, *args, **kwargs):
        if not self.contact_exists(self.connection):
            raise Http404
        poll_topics = self.get_polls_for_contact(self.connection.contact)
        return self.create_json_response(
            {"success": True, "poll_topics": poll_topics})

    def get_polls_for_contact(self, contact):
        poll_topics = []
        for poll in contact.polls.filter(start_date__isnull=False, end_date__isnull=True):
            poll_topics.append({"poll_id": poll.id, "label": poll.name})
        return poll_topics