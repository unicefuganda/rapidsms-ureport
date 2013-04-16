from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from ureport.tests.functional.splinter_wrapper import SplinterTestCase

BROWSER = Browser('firefox')


class PollViewTest(SplinterTestCase):
    #fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = BROWSER
        self.open('/')

    def tearDown(self):
        pass
        #self.open('/account/logout')

    def test_something_simple(self):
        self.assertTrue(False)