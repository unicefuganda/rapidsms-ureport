from splinter import Browser
from poll.models import Poll
from poll.tests import TestScript
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure
from ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table
from ureport.tests.functional.create_poll_utils import get_incoming_message


class UreportTest(SplinterTestCase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = Browser()
        self.poll, self.connections_list = start_poll_queues_messages_in_table()

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_that_poll_status_changes_when_started(self):
        self.create_and_sign_in_admin("argha", "a")
        self.open("/view_poll/%s" % self.poll.id)
        self.browser.find_link_by_text('Start Poll').first.click()
        assert self.browser.is_text_present('Close Poll')

        newly_added_poll = Poll.objects.get(id=self.poll.id)
        assert newly_added_poll.start_date is not None

        self.assert_that_poll_questions_are_sent_out_to_contacts(poll=newly_added_poll)
        self.assert_that_contacts_can_respond_to_poll(newly_added_poll)

    def assert_that_poll_questions_are_sent_out_to_contacts(self, poll):
        self.assertEquals(poll.messages.count(), 2)
        self.assertEquals(poll.messages.all()[0].text, poll.question)
        self.assertEquals(poll.messages.all()[1].text, poll.question)
        self.assertEquals(poll.messages.filter(status='Q').count(), 2)
        self.assertEquals(poll.messages.filter(status='Q')[0].text, poll.question)
        self.assertEquals(poll.messages.filter(status='Q')[1].text, poll.question)

    def assert_that_contacts_can_respond_to_poll(self,poll):
       poll.process_response(get_incoming_message(self.connections_list[0],"yes"))
       poll.process_response(get_incoming_message(self.connections_list[1],"no"))
       self.assertEquals(poll.responses.count(), 2)
       self.open('/mypolls/12/')

       assert self.browser.find_link_by_href('/%s/responses/' % self.poll.id)
       assert self.browser.is_text_present(' Responses (%i)' % poll.responses.count())
       






