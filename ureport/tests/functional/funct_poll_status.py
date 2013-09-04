from splinter import Browser
import time
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure


class PollStatusTest(SplinterTestCase):
    def go_to_poll_status_page(self, poll_id):
        poll_status_url = "/poll_status/%s" % poll_id
        self.create_and_sign_in_admin("argha", "a", poll_status_url)

    def setUp(self):
        self.browser = Browser()

        self.poll, self.connections_list = start_poll_queues_messages_in_table()

        self.poll.add_yesno_categories()

    def tearDown(self):
        self.browser.quit()

    @take_screenshot_on_failure
    def test_should_show_the_status_page(self):
        self.go_to_poll_status_page(self.poll.id)
        # self.assertEqual(self.browser.is_element_present_by_id('poll-details'), True)
        # self.assertTrue(str(self.poll.id) in self.browser.find_by_id("poll-details").first.text)
        time.sleep(10)
        self.assertEqual(self.browser.find_by_id('contact-count').text, "2")
        self.assertEqual(self.browser.find_by_id('category-count').text, "3")
        self.assertEqual(self.browser.find_by_id('is-yesno').text, "yes")