from poll.models import Poll
from poll.tests.TestScript import fake_incoming
from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure
from ureport_project.rapidsms_ureport.ureport.tests.functional.create_poll_for_tests import start_poll_queues_messages_in_table
from ureport_project.rapidsms_ureport.ureport.tests.functional.create_poll_utils import get_browser


class UreportTest(SplinterTestCase):
    fixtures = ['0004_migration_initial_data.json']

    def setUp(self):
        self.browser = get_browser()
        self.open('/')
        self.poll_id, self.contacts_count = start_poll_queues_messages_in_table()

    def tearDown(self):
        self.open('/account/logout')
        self.browser.quit()

    def test_that_poll_status_changes_when_started(self):
        self.create_and_sign_in_admin("argha", "a")
        self.open("/view_poll/%s" % self.poll_id)
        self.browser.find_link_by_text('Start Poll').first.click()
        assert self.browser.is_text_present('Close Poll')
        newly_added_poll = Poll.objects.get(id=self.poll_id)
        self.assertThat(newly_added_poll.start_date is not None)

    @take_screenshot_on_failure
    def test_should_match_poll_question_to_message_text(self):
        newly_added_poll = Poll.objects.get(id=self.poll_id)

        self.test_that_poll_status_changes_when_started()

        self.assertEquals(newly_added_poll.messages.count(), 2)
        self.assertEquals(newly_added_poll.messages.all()[0].text, newly_added_poll.question)
        self.assertEquals(newly_added_poll.messages.all()[1].text, newly_added_poll.question)

        self.assertEquals(newly_added_poll.messages.filter(status='Q').count(), 2)
        self.assertEquals(newly_added_poll.messages.filter(status='Q')[0].text, newly_added_poll.question)
        self.assertEquals(newly_added_poll.messages.filter(status='Q')[1].text, newly_added_poll.question)
    #
    # def test_ureporter_can_respond_to_poll_question(self):
    #     fake_incoming()




