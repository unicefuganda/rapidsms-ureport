from poll.models import Poll
from ureport.tests.functional.create_poll_utils import get_incoming_message
from ureport.tests.functional.poll_assertions import PollAssertions


class PollBase(PollAssertions):

    def start_poll(self):
        poll_url = "/view_poll/%s" % self.poll.id
        self.create_and_sign_in_admin("argha", "a", poll_url)

        self.assertTrue(self.browser.is_text_present('Start Poll', 10))
        self.browser.find_link_by_text('Start Poll').first.click()

        assert self.browser.is_text_present('Close Poll')

    def get_poll(self, poll_id):
        return Poll.objects.get(id=poll_id)

    def respond_to_poll(self, poll):
        poll.process_response(get_incoming_message(self.connections_list[0],"yes"))
        poll.process_response(get_incoming_message(self.connections_list[1],"no"))

    def go_to_poll_report_page(self, poll):
        self.open('/polls/%s/report/' % poll.id)

    def get_poll_response_location(self, response):
        contact = response.message.connection.contact
        location = contact.reporting_location
        return location.name

    def get_first_poll_response_location(self, poll):
        responses = self.get_poll_responses(poll)
        return self.get_poll_response_location(responses[0])

    def get_poll_responses(self, poll):
        responses = poll.responses.all()
        return responses





