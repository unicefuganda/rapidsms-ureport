import time

from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from poll.models import Poll
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from ureport_project.rapidsms_ureport.ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table
from ureport_project.rapidsms_ureport.ureport.tests.functional.create_poll_utils import get_browser


class UreportTest(SplinterTestCase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = get_browser()
        self.open('/')

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_should_match_poll_question_to_message_text(self):
        self.poll_id, self.contacts_count = start_poll_queues_messages_in_table(self)

        newly_added_poll = Poll.objects.get(id=self.poll_id)

        time.sleep(3)

        self.assertEquals(newly_added_poll.messages.count(), 2)
        self.assertEquals(newly_added_poll.messages.all()[0].text, newly_added_poll.question)
        self.assertEquals(newly_added_poll.messages.all()[1].text, newly_added_poll.question)

        self.assertEquals(newly_added_poll.messages.filter(status='Q').count(), 2)
        self.assertEquals(newly_added_poll.messages.filter(status='Q')[0].text, newly_added_poll.question)
        self.assertEquals(newly_added_poll.messages.filter(status='Q')[1].text, newly_added_poll.question)


