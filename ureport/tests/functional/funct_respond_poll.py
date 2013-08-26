from splinter import Browser
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table


class PollRespondTest(PollBase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = Browser()
        self.poll, self.connections_list = start_poll_queues_messages_in_table()

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_that_user_can_respond_to_a_poll(self):
        self.start_poll()
        self.respond_to_poll(self.poll)

        self.assert_that_poll_has_responses(self.poll)
