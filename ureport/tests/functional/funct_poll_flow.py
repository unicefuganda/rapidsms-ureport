from splinter import Browser
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form, rows_of_table_by_class
from ureport.tests.functional.poll_base import PollBase


class PollFlowTest(PollBase):
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

    def test_that_poll_status_changes_when_started(self):
        poll_id, question = self.setup_poll()

        self.open("/poll_status/%s" % poll_id)
        self.start_poll(poll_id)

        assert self.browser.is_text_present('Close Poll')
        self.assert_that_poll_start_date_is_not_none(poll_id)


    def test_that_poll_can_be_sent_out_to_contacts(self):
        poll_id, question = self.setup_poll()

        self.start_poll(poll_id)

        number_of_contact_for_poll = 2
        question = 'What is your name'

        self.assert_that_poll_question_are_sent_out_to_contacts(number_of_contact_for_poll, question)


    def test_that_polls_can_be_responded(self):
        poll_id, question = self.setup_poll()
        self.start_poll(poll_id)

        self.open('/router/console/')
        number_of_responses = len(rows_of_table_by_class(self.browser, "messages module"))

        self.respond_to_the_started_poll("0794339344", "yes")
        self.respond_to_the_started_poll("0794339345", "no")
        increment = 2
        self.assert_that_number_of_responses_increase_by(number_of_responses, increment)

    def test_that_polls_can_be_reopen(self):
        poll_id, question = self.setup_poll()
        self.open("/view_poll/%s" % poll_id)
        self.start_poll(poll_id)
        self.close_poll(poll_id)
        self.browser.find_link_by_text('Reopen Poll').first.click()
        self.assert_that_poll_end_date_is_none(poll_id)

    def test_that_admin_is_able_to_add_new_poll(self):
        poll_id, question = self.setup_poll()
        self.open('/mypolls/%s' % poll_id)

        self.assert_that_page_has_add_poll_button()

    def test_should_show_the_status_page(self):
        poll_id, question = self.setup_poll()
        self.start_poll(poll_id)

        self.open("/poll_status/%s" % poll_id)
        self.assertEqual(self.browser.is_element_present_by_id('poll-details'), True)
        self.assertTrue(poll_id in self.browser.find_by_id("poll-details").first.text)

        self.assertEqual(self.browser.find_by_id('contact-count').text, "2")
        self.assertEqual(self.browser.find_by_id('category-count').text, "3")
        self.assertEqual(self.browser.find_by_id('is-yesno').text, "yes")