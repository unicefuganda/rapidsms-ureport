import datetime
from poll.models import Poll
from ureport.tests.functional.create_poll_utils import get_incoming_message
from ureport.tests.functional.admin_helper import fill_form
from ureport.tests.functional.poll_assertions import PollAssertions


class PollBase(PollAssertions):

    def start_poll_through_poll_page(self):
        self.log_as_admin_and_visit("/view_poll/%s" % self.poll.id)

        self.assertTrue(self.browser.is_text_present('Start Poll', 10))
        self.browser.find_link_by_text('Start Poll').first.click()

    def start_poll(self):
        if not self.poll.start_date:
            self.poll.start()

        if self.poll.end_date is not None:
            self.poll.end_date = None
            self.poll.save()

    def close_poll(self):
        if not self.poll.start_date:
            self.poll.start()
        self.poll.end_date = datetime.datetime.now().date()
        self.poll.save()

    def log_in_as_ureport(self):
        self.open('/accounts/login')
        self.browser.fill("username", "ureport")
        self.browser.fill("password", "ureport")
        self.browser.find_by_css("input[type=submit]").first.click()

    def log_as_admin_and_visit(self, url):
        self.create_and_sign_in_admin("ureport", "ureport", url)

    def get_poll(self, poll_id):
        return Poll.objects.get(id=poll_id)

    def respond_to_poll(self, poll):
        poll.process_response(get_incoming_message(self.connections_list[0],"yes"))
        poll.process_response(get_incoming_message(self.connections_list[1],"no"))

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

    def create_poll(self, name, type, question, group):
        self.open("/createpoll")
        form_data = {
            "id_type": type,
            "id_name": name,
            "id_groups": group
        }
        self.browser.fill("question_en", question)
        fill_form(self.browser, form_data)
        self.browser.find_by_css(".buttons a").last.click()
        return self.browser.url.split('/')[-2]




