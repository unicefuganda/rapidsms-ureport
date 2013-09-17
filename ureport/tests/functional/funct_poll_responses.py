from splinter import Browser
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure
from ureport.tests.functional.admin_base import AdminBase
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form


class PollResponsesTest(PollBase, AdminBase):

    def setUp(self):
        self.browser = Browser()
        self.log_in_as_ureport()

    def cleanup(self, url):
        self.open(url)

        if self.browser.is_element_present_by_id("action-toggle"):
            fill_form(self.browser, {"action-toggle": True})
            fill_form_and_submit(self.browser, {"action": "delete_selected"}, "index", True, True)

            is_confirmation_present= self.browser.is_element_present_by_value("Yes, I'm sure")
            self.assertTrue(is_confirmation_present)

            self.browser.find_by_value("Yes, I'm sure").first.click()

    def tearDown(self):
        self.cleanup("/admin/poll/poll/")
        self.cleanup("/admin/rapidsms/connection/")
        self.cleanup("/admin/rapidsms/backend/")
        self.cleanup("/admin/rapidsms/contact/")
        self.cleanup("/admin/auth/group/")
        #TODO: when deleting users don't delete the "ureport" and "admin" ones
        # self.cleanup("/admin/auth/user/")

        self.browser.quit()

    @take_screenshot_on_failure
    def test_that_poll_responses_are_shown_up_at_report_page(self):
        self.create_group("groupFT")
        self.create_backend("console")
        self.create_contact("FT1", "Male", "console", "0794339344", "groupFT")
        self.create_contact("FT2", "Female", "console", "0794339345", "groupFT")

        poll_id = self.create_poll("Some poll", "Yes/No Question", "What is your name", "groupFT")
        self.start_poll(poll_id)
        self.respond_to_the_started_poll("0794339344", "yes")

        #
        # self.log_as_admin_and_visit('/polls/%s/report/' % self.poll.id)
        #
        # self.assert_that_question_is(self.poll.question)
        # self.assert_the_number_of_participants_of_the_poll_is(self.poll.responses)
        #
        # location = self.get_first_poll_response_location(self.poll)
        # self.assert_that_response_location_is(location)
        #
        # self.assert_that_number_of_responses_is(self.poll.responses)