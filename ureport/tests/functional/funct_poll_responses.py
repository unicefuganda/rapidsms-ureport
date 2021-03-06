import unittest
import time
from ureport.tests.functional.poll_assertions import PollAssertions
from ureport.tests.functional.splinter_wrapper import SplinterWrapper
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form
from ureport.tests.functional.admin_base import AdminBase
from ureport.tests.functional.clean_helper import login_as_admin, build_url, post


class PollResponsesTest(unittest.TestCase, PollAssertions):
    browser = SplinterWrapper.getBrowser()

    def tearDown(self):
        responses = PollBase.get_poll_responses_ids(self.browser, self.poll_id)
        for response in responses:
            delete_responses_url = build_url('/polls/responses/%s/delete/' % response.value)
            post(self.opener, delete_responses_url)
        PollBase.close_poll(self.poll_id)

    @classmethod
    def setUpClass(cls):
        AdminBase.log_in_as_ureport()
        cls.poll_id, cls.question = PollBase.setup_poll(cls.browser,question="This is a new poll.")
        AdminBase.change_users_group("groupFT")
        cls.opener = login_as_admin('ureport','ureport')

    @classmethod
    def cleanup(cls, url):
        SplinterWrapper.open(url)
        if cls.browser.is_element_present_by_id("action-toggle"):
            fill_form(cls.browser, {"action-toggle": True})
            fill_form_and_submit(cls.browser, {"action": "delete_selected"}, "index", True, True)
            cls.browser.find_by_value("Yes, I'm sure").first.click()

    @classmethod
    def delete_poll(cls):
        delete_url = build_url('/polls/%s/delete/' % cls.poll_id)
        post(cls.opener, delete_url)

    @classmethod
    def tearDownClass(cls):
        cls.delete_poll()
        cls.cleanup("/admin/rapidsms/connection/")
        cls.cleanup("/admin/rapidsms/backend/")
        cls.cleanup("/admin/rapidsms/contact/")
        cls.cleanup("/admin/auth/group/")

    def test_that_poll_responses_are_shown_up_at_report_page(self):
        PollBase.start_poll(self.browser,self.poll_id)

        PollBase.respond_to_the_started_poll("0794339344", "yes")
        SplinterWrapper.open('/polls/%s/report/' % self.poll_id)
        self.assert_that_question_is(self.question)
        self.assert_the_number_of_participants_of_the_poll_is(1)

        self.assert_that_response_location_is("Kasese")
        self.assert_that_number_of_responses_is(1)

    def test_that_a_poll_response_can_be_reassigned_to_another_poll(self):
        second_poll_id = PollBase.create_poll(self.browser,name='Second Poll',type="Yes/No Question",question="Is the first poll working?",group="groupFT")
        PollBase.start_poll(self.browser,second_poll_id)

        PollBase.respond_to_the_started_poll("0794339344", "yes")
        PollBase.close_poll(second_poll_id)

        PollBase.reassign_poll_response(second_poll_id,self.poll_id)
        time.sleep(2) #Takes a time for a poll to be reassigned
        PollBase.start_poll(self.browser,self.poll_id)

        SplinterWrapper.open('/polls/%s/report/' % self.poll_id)
        self.assert_that_number_of_responses_is(1)

    def test_that_a_response_can_be_replied_to_an_ureporter(self):
        message = "Hello"
        PollBase.start_poll(self.browser,self.poll_id)
        number_of_responses = PollBase.respond_to_the_started_poll("0794339344", "yes")
        self.assert_that_number_of_responses_increase_by(number_of_responses, 1)

        PollBase.reply_poll_to_an_ureporter(self.poll_id, message)
        self.assert_that_message_has_been_sent_out_to_ureporter(message)

