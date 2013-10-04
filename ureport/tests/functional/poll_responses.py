from splinter import Browser
from splinter_wrapper import SplinterTestCase
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form
from ureport.tests.functional.admin_base import AdminBase


def disabled(f):
    f.__test__ = False
    return f


class PollResponsesTest(PollBase):
    browser = Browser()
    AdminBase.log_in_as_ureport(browser)
    poll_id, question = PollBase.setup_poll(browser)

    @classmethod
    def setUpClass(cls):
        PollBase.start_poll(cls.browser,cls.poll_id)

    @classmethod
    def cleanup(cls, url):
        SplinterTestCase.open(cls.browser,url)

        if cls.browser.is_element_present_by_id("action-toggle"):
            fill_form(cls.browser, {"action-toggle": True})
            fill_form_and_submit(cls.browser, {"action": "delete_selected"}, "index", True, True)
            cls.browser.find_by_value("Yes, I'm sure").first.click()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup("/admin/poll/poll/")
        cls.cleanup("/admin/rapidsms/connection/")
        cls.cleanup("/admin/rapidsms/backend/")
        cls.cleanup("/admin/rapidsms/contact/")
        cls.cleanup("/admin/auth/group/")
        cls.browser.quit()

    # def test_that_poll_responses_are_shown_up_at_report_page(self):
    #     self.respond_to_the_started_poll("0794339344", "yes")
    #     self.respond_to_the_started_poll("0794339345", "no")
    #     SplinterTestCase.open(self.browser,'/polls/%s/report/' % self.poll_id)
    #
    #     self.assert_that_question_is(self.question)
    #     self.assert_the_number_of_participants_of_the_poll_is(2)
    #
    #     self.assert_that_response_location_is(REPORTING_LOCATION_KAMAIBA_DISTRICT)
    #     self.assert_that_number_of_responses_is(2)

    # def test_that_a_poll_response_can_be_reassigned_to_another_poll(self):
    #     AdminBase.create_contact(self.browser,"FT3", "Male", "console", "%s4" % "999", "groupFT")
    #     AdminBase.create_contact(self.browser,"FT4", "Male", "console", "%s4" % "999", "groupFT")
    #     second_poll_id = PollBase.create_poll(self.browser,name='Second Poll',type="Yes/No Question",question="Is the first poll working?",group="groupFT")
    #     self.change_users_group("groupFT")
    #     self.respond_to_the_started_poll("0794339344", "yes")
    #     self.respond_to_the_started_poll("0794339345", "no")
    #     self.close_poll(self.poll_id)
    #     PollBase.start_poll(self.browser,second_poll_id)
    #     self.reassign_poll_response(self.poll_id, second_poll_id)
    #     SplinterTestCase.open(self.browser,'/polls/%s/report/' % second_poll_id)
    #     self.assert_that_number_of_responses_is(2)

    def test_that_a_response_can_be_replied_to_an_ureporter(self):
        message = "Hello"
        self.change_users_group("groupFT")
        self.respond_to_the_started_poll("0794339344", "yes")
        self.reply_poll_to_an_ureporter(self.poll_id, message)

        self.assert_that_message_has_been_sent_out_to_ureporter(message)