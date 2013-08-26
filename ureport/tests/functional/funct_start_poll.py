from splinter import Browser
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table


class UreportTest(PollBase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = Browser()
        self.poll, self.connections_list = start_poll_queues_messages_in_table()

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_that_poll_status_changes_when_started(self):
        self.start_poll()

        newly_added_poll = self.get_poll(self.poll.id)

        self.assert_that_poll_start_date_is_not_none(newly_added_poll)
        self.assert_that_poll_questions_are_sent_out_to_contacts(poll=newly_added_poll)

        self.respond_to_poll(newly_added_poll)
        self.assert_that_poll_has_responses(newly_added_poll)

