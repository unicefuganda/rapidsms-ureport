from splinter import Browser
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form
from ureport.tests.functional.admin_base import AdminBase, REPORTING_LOCATION_KAMAIBA_DISTRICT

class PollResponsesTest(PollBase, AdminBase):

    def setUp(self):
        self.browser = Browser()
        self.log_in_as_ureport()

    def cleanup(self, url):
        self.open(url)

        if self.browser.is_element_present_by_id("action-toggle"):
            fill_form(self.browser, {"action-toggle": True})
            fill_form_and_submit(self.browser, {"action": "delete_selected"}, "index", True, True)
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


    def test_that_poll_responses_are_shown_up_at_report_page(self):
        poll_id, question = self.setup_poll()

        self.start_poll(poll_id)
        self.respond_to_the_started_poll("0794339344", "yes")
        self.respond_to_the_started_poll("0794339345", "no")

        self.open('/polls/%s/report/' % poll_id)

        self.assert_that_question_is(question)
        number_of_responses = number_of_participants= 2
        self.assert_the_number_of_participants_of_the_poll_is(number_of_participants)

        self.assert_that_response_location_is(REPORTING_LOCATION_KAMAIBA_DISTRICT)
        self.assert_that_number_of_responses_is(number_of_responses)

    def test_that_a_poll_response_can_be_reassigned_to_another_poll(self):
        first_poll_id, first_question = self.setup_poll()
        second_poll_id, second_question = self.setup_poll(question="Is the first poll working?", number_prefix="999")
        self.start_poll(first_poll_id)
        group_name = "groupFT"
        self.change_users_group(group_name)
        self.respond_to_the_started_poll("0794339344", "yes")
        self.respond_to_the_started_poll("0794339345", "no")
        self.close_poll(first_poll_id)
        self.start_poll(second_poll_id)
        self.reassign_poll_response(first_poll_id,second_poll_id)
        self.open('/polls/%s/report/' % second_poll_id)
        self.assert_that_number_of_responses_is(2)