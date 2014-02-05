from django.http import HttpResponseNotAllowed
from ureport.views.api.base import UReporterApiView


class PollSummary(UReporterApiView):
    def get(self, request, *args, **kwargs):
        if self.contact_exists(self.connection):
            poll_id = kwargs.get("poll_id")
            poll = self.get_poll(poll_id)
            poll_summary = self.get_poll_summary(poll)
            return self.create_json_response({"success" : True, "poll_result": poll_summary})
        else:
            return self.create_json_response({"success": False, "reason": "Ureporter not found"}, status_code=404)

    def get_responses_summary_for_poll(self, poll):
        responses_by_category = poll.responses_by_category()
        categorized_responses_list = []
        for data in responses_by_category:
            categorized_responses_list.append({"name": data['category__name'], "count": data['value']})
        return categorized_responses_list

    def get_poll_summary(self, poll):
        total_responses = poll.responses.count()
        responses_summary = self.get_responses_summary_for_poll(poll)
        total_categorized_responses = self.get_total_categorized_responses(responses_summary)
        data = { "total_responses" : total_responses,
                "total_categorized_responses" : total_categorized_responses,
                "responses" : responses_summary}
        return data

    def get_total_categorized_responses(self, responses):
        return sum(response['count'] for response in responses)

    def post(self, request, *args, **kwargs):
        return HttpResponseNotAllowed("Method Not Allowed")