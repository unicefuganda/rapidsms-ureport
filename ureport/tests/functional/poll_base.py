import datetime
from poll.models import Poll
from ureport.tests.functional.create_poll_utils import get_incoming_message
from ureport.tests.functional.poll_assertions import PollAssertions
from ureport.tests.functional.admin_helper import fill_form, rows_of_table_by_class


class PollBase(PollAssertions):

    def start_poll_through_poll_page(self):
        self.log_as_admin_and_visit("/view_poll/%s" % self.poll.id)

        self.assertTrue(self.browser.is_text_present('Start Poll', 10))
        self.browser.find_link_by_text('Start Poll').first.click()
        self.assertTrue(self.browser.is_text_present('Close Poll', 10))

    def start_poll(self, poll_id):
        self.open("/view_poll/%s" % poll_id)

        self.assertTrue(self.browser.is_text_present('Start Poll', 10))
        self.browser.find_link_by_text('Start Poll').first.click()
        self.assertTrue(self.browser.is_text_present('Close Poll', 10))

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
        self.assert_create_poll_is_present()

        self.browser.find_by_css(".buttons a").last.click()
        return self.browser.url.split('/')[-2]

    def respond_to_the_started_poll(self, sender, message):
        self.open('/router/console/')
        rows_responses = rows_of_table_by_class(self.browser, "messages module")
        number_of_responses = len(rows_responses)

        form_data = {
            "text": message,
            "sender": sender
        }
        fill_form(self.browser, form_data, True)
        self.browser.find_by_css("input[type=submit]").first.click()

        self.assert_that_number_of_responses_increase_by_one(number_of_responses)



