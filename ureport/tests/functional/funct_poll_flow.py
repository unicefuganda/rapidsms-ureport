from splinter import Browser
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table

class PollFlowTest(PollBase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = Browser()
        self.poll, self.connections_list = start_poll_queues_messages_in_table()


    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_that_poll_status_changes_when_started(self):
        self.start_poll_through_poll_page()

        assert self.browser.is_text_present('Close Poll')
        self.assert_that_poll_start_date_is_not_none(self.get_poll(self.poll.id))

    def test_that_poll_can_be_sent_out_to_contacts(self):
        self.start_poll()
        newly_added_poll = self.get_poll(self.poll.id)

        self.assert_that_poll_questions_are_sent_out_to_contacts(poll=newly_added_poll)

    def test_that_polls_can_be_responded(self):
        self.start_poll()
        newly_added_poll = self.get_poll(self.poll.id)

        self.respond_to_poll(newly_added_poll)
        self.log_as_admin_and_visit('/mypolls/%s' % self.poll.id)

        self.assert_that_poll_has_responses(newly_added_poll)

    def test_that_polls_can_be_reopen(self):
        self.close_poll()
        self.log_as_admin_and_visit("/view_poll/%s" % self.poll.id)

        self.browser.find_link_by_text('Reopen Poll').first.click()
        self.assert_that_poll_end_date_is_none(self.get_poll(self.poll.id))

    def test_that_admin_is_able_to_add_new_poll(self):
        self.log_as_admin_and_visit('/mypolls/%s' % self.poll.id)

        self.assert_that_page_has_add_poll_button()

    def test_should_show_the_status_page(self):
        self.poll.add_yesno_categories()
        self.log_as_admin_and_visit("/poll_status/%s" % self.poll.id)

        self.assertEqual(self.browser.is_element_present_by_id('poll-details'), True)
        self.assertTrue(str(self.poll.id) in self.browser.find_by_id("poll-details").first.text)

        self.assertEqual(self.browser.find_by_id('contact-count').text, "2")
        self.assertEqual(self.browser.find_by_id('category-count').text, "3")
        self.assertEqual(self.browser.find_by_id('is-yesno').text, "yes")