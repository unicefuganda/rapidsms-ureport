import time
from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from ureport.tests.functional.create_polls_for_view_poll import create_polls
from ureport.tests.functional.splinter_wrapper import SplinterTestCase

BROWSER = Browser('firefox')


class PollViewTest(SplinterTestCase):

    def setUp(self):
        self.browser = BROWSER
        self.open('/')

    def tearDown(self):
        self.browser.quit()

    def test_should_show_poll_list_when_there_are_polls_with_responses(self):

        polls = create_polls(11)
        for poll in polls:
            poll.start()
            assert(poll.messages.count() > 0)

        self.create_and_sign_in_admin("ureport", "ureport")
        time.sleep(5)

        self.assertTrue(self.browser.is_element_present_by_css("div[class=poll_list]"))
