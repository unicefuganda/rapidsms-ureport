from ureport.tests.functional.create_poll_utils import get_incoming_message
from ureport.tests.functional.splinter_wrapper import SplinterTestCase


class PollAssertions(SplinterTestCase):
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

    def assert_that_poll_start_date_is_not_none(self, poll):
        assert poll.start_date is not None
