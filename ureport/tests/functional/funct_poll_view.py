from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from ureport_project.rapidsms_ureport.ureport.tests.functional.create_poll_utils import get_browser, create_fake_response
from ureport_project.rapidsms_ureport.ureport.tests.functional.create_polls_for_view_poll import create_polls_with_fake_responses


class PollViewTest(SplinterTestCase):

    def setUp(self):
        self.browser = get_browser()
        self.open('/')

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_poll_view_should_show_only_ten_polls(self):
        polls = create_polls_with_fake_responses(11)
        for poll in polls:
            poll.start()
            for contact in poll.contacts.all():
                create_fake_response(contact.default_connection, 'yes')

            assert(poll.messages.count() > 0)
            poll.end()

        self.create_and_sign_in_admin("ureport", "ureport")

        poll_list = self.browser.find_by_id("poll_record")

        # self.assertTrue(self.browser.is_element_present_by_id("poll_record"))
