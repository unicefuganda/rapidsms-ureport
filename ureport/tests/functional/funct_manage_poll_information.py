from splinter import Browser
import time
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table

class ManagePollInformationTest(PollBase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = Browser()
        self.poll, self.connections_list = start_poll_queues_messages_in_table()

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_that_admin_can_edit_a_poll(self):
        self.start_poll()
        poll = self.get_poll(self.poll.id)
        self.respond_to_poll(poll)

        self.log_as_admin_and_visit("/mypolls/%s/" % self.poll.id)
        self.assert_that_page_has_edit_poll_button(self.poll)

