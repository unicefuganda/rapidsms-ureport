from splinter import Browser
from ureport.tests.functional.admin_base import AdminBase
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form

class PollFlowTest(PollBase, AdminBase):

    @take_screenshot_on_failure
    def setUp(self):
        self.browser = Browser()
        self.log_in_as_ureport()

    def cleanup(self, url):
        self.open(url)
        
        if self.browser.is_element_present_by_id("action-toggle"):
            fill_form(self.browser, {"action-toggle": True})
            fill_form_and_submit(self.browser, {"action": "delete_selected"}, "index", True, True)
            self.browser.find_by_value("Yes, I'm sure").first.click()

    @take_screenshot_on_failure
    def tearDown(self):

        self.cleanup("/admin/poll/poll/")
        self.cleanup("/admin/rapidsms/connection/")
        self.cleanup("/admin/rapidsms/backend/")
        self.cleanup("/admin/rapidsms/contact/")
        self.cleanup("/admin/auth/group/")
        #TODO: when deleting users don't delete the "ureport" and "admin" ones
        # self.cleanup("/admin/auth/user/")

        self.browser.quit()

    # def test_that_poll_status_changes_when_started(self):
    #     self.start_poll_through_poll_page()
    #
    #     assert self.browser.is_text_present('Close Poll')
    #     self.assert_that_poll_start_date_is_not_none(self.get_poll(self.poll.id))

    # def test_that_poll_can_be_sent_out_to_contacts(self):
    #     self.start_poll()
    #     newly_added_poll = self.get_poll(self.poll.id)
    #
    #     self.assert_that_poll_questions_are_sent_out_to_contacts(poll=newly_added_poll)
    #
    # def test_that_polls_can_be_responded(self):
    #     self.start_poll()
    #     newly_added_poll = self.get_poll(self.poll.id)
    #
    #     self.respond_to_poll(newly_added_poll)
    #     self.log_as_admin_and_visit('/mypolls/%s' % self.poll.id)
    #
    #     self.assert_that_poll_has_responses(newly_added_poll)
    #
    # def test_that_polls_can_be_reopen(self):
    #     self.close_poll()
    #     self.log_as_admin_and_visit("/view_poll/%s" % self.poll.id)
    #
    #     self.browser.find_link_by_text('Reopen Poll').first.click()
    #     self.assert_that_poll_end_date_is_none(self.get_poll(self.poll.id))
    #
    # def test_that_admin_is_able_to_add_new_poll(self):
    #     self.log_as_admin_and_visit('/mypolls/%s' % self.poll.id)
    #
    #     self.assert_that_page_has_add_poll_button()

    @take_screenshot_on_failure
    def test_should_show_the_status_page(self):
        self.create_group("groupFT")
        self.create_backend("console")
        self.create_contact("FT1", "Male", "console", "0794339344", "groupFT")
        self.create_contact("FT2", "Female", "console", "0794339345", "groupFT")

        poll_id = self.create_poll("Some poll", "Yes/No Question", "What is your name", "groupFT")

        self.open("/poll_status/%s" % poll_id)

        self.assertEqual(self.browser.is_element_present_by_id('poll-details'), True)
        self.assertTrue(poll_id in self.browser.find_by_id("poll-details").first.text)

        self.assertEqual(self.browser.find_by_id('contact-count').text, "2")
        self.assertEqual(self.browser.find_by_id('category-count').text, "3")
        self.assertEqual(self.browser.find_by_id('is-yesno').text, "yes")
