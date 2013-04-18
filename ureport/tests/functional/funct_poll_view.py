from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from poll.models import Poll
from ureport.tests.functional.create_polls_for_view_poll import create_eleven_polls_for_view_polls
from ureport.tests.functional.splinter_wrapper import SplinterTestCase

BROWSER = Browser('firefox')


class PollViewTest(SplinterTestCase):

    #fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = BROWSER
        self.open('/')

    def tearDown(self):
        self.browser.quit()

    def test_should_show_only_ten_polls_on_view_polls_initially(self):
        create_eleven_polls_for_view_polls()