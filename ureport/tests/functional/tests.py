from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from rapidsms_httprouter.models import Message, MessageBatch
from poll.models import Poll
from ureport.tests.functional.login_page import login_succeeds_with_super_user, login_fails_without_user
from ureport.tests.functional.about_page import about_ureport_page
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table
from ureport.tests.functional.join_page import join_page
from ureport.tests.functional.home_page import home_page, home_page_visualisation, home_page_map, best_viz
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from django.db import connection

BROWSER = Browser('firefox')


class UreportTest(SplinterTestCase):

    def setUp(self):
        self.browser = BROWSER
        self.open('/')

    def tearDown(self):
        self.open('/account/logout')

    def test_should_match_poll_question_to_message_text(self):
        sql_text = "select text from rapidsms_httprouter_message where status='Q'"
        self.poll_id, self.contacts_count = start_poll_queues_messages_in_table(self)
        self.cursor = connection.cursor()

        self.cursor.execute(sql_text)
        newly_added_poll = Poll.objects.get(id=self.poll_id)

        self.assertEquals(newly_added_poll.messages.count(),2)
        self.assertEquals(newly_added_poll.messages.all()[0].text,newly_added_poll.question)
        self.assertEquals(newly_added_poll.messages.all()[1].text,newly_added_poll.question)

        self.assertEquals(newly_added_poll.messages.filter(status='Q').count(),2)
        self.assertEquals(newly_added_poll.messages.filter(status='Q')[0].text,newly_added_poll.question)
        self.assertEquals(newly_added_poll.messages.filter(status='Q')[1].text,newly_added_poll.question)


    @classmethod
    def tearDownClass(cls):
        BROWSER.quit()



    # def test_best_viz(self):
    #     best_viz(self)

    # def test_home_page(self):
    #     home_page(self)
    #
    # def test_home_page_visualisation(self):
    #     home_page_visualisation(self)
    #
    # def test_home_page_map(self):
    #     home_page_map(self)
    #
    # def test_join_page(self):
    #     join_page(self)


    # def test_about_page(self):
    #     about_ureport_page(self)
    #
    # def test_login_for_admin(self):
    #     login_succeeds_with_super_user(self)
    #
    # def test_login_fails_for_non_user(self):
    #     login_fails_without_user(self)

