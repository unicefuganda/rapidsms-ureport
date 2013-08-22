from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from rapidsms_ureport.ureport.tests.functional.create_poll_utils import create_fake_response, get_browser
from rapidsms_ureport.ureport.tests.functional.create_polls_for_view_poll import create_polls_with_fake_responses
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure


class PollViewTest(SplinterTestCase):

    def setUp(self):
        self.browser = Browser()

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    @take_screenshot_on_failure
    def test_poll_view_should_show_only_ten_polls(self):
        polls = create_polls_with_fake_responses(11)
        for poll in polls:
            poll.start()
            for contact in poll.contacts.all():
                create_fake_response(contact.default_connection, 'yes')

            assert(poll.messages.count() > 0)
            poll.end()

        self.create_and_sign_in_admin("ureport", "ureport")

        self.browser.find_by_id("poll_record")