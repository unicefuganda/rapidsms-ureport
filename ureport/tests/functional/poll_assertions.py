from ureport.tests.functional.create_poll_utils import get_incoming_message
from ureport.tests.functional.splinter_wrapper import SplinterTestCase

ANY_POLL_ID = '12'


class PollAssertions(SplinterTestCase):
    def assert_that_poll_questions_are_sent_out_to_contacts(self, poll):
        self.assertEquals(poll.messages.count(), 2)
        self.assertEquals(poll.messages.all()[0].text, poll.question)
        self.assertEquals(poll.messages.all()[1].text, poll.question)
        self.assertEquals(poll.messages.filter(status='Q').count(), 2)
        self.assertEquals(poll.messages.filter(status='Q')[0].text, poll.question)
        self.assertEquals(poll.messages.filter(status='Q')[1].text, poll.question)

    def assert_that_poll_start_date_is_not_none(self, poll):
        assert poll.start_date is not None

    def assert_that_poll_has_responses(self, poll):
        self.assertEquals(poll.responses.count(), 2)
        self.open('/mypolls/%s' % ANY_POLL_ID)

        elements = self.browser.find_link_by_href('/%s/responses/' % self.poll.id)
        assert elements.first.value == 'Responses (%i)' % poll.responses.count()