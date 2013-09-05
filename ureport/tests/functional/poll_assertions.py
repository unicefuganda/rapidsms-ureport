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

        elements = self.browser.find_link_by_href('/%i/responses/' % poll.id)
        assert elements.first.value == 'Responses (%i)' % poll.responses.count()

    def assert_that_question_is(self, question):

        elements = self.browser.find_by_xpath('//*[@class="question"]')
        assert elements.first.value == question

    def assert_the_number_of_participants_of_the_poll_is(self, responses):
        elements = self.browser.find_by_xpath('//*[@class="participants"]')
        num_participants = elements.first.value.split(' ')[0]

        self.assertEquals(int(num_participants), responses.count())

    def assert_that_response_location_is(self, location):
        elements = self.browser.find_by_xpath('//*[@class="poll_table"]')
        tbody = elements.find_by_tag('tbody')
        trs = tbody.find_by_tag('tr')
        tds = trs.find_by_tag('td')

        self.assertEquals(tds.first.value, location)

    def assert_that_number_of_responses_is(self,responses):

        elements = self.browser.find_by_xpath('//*[@class="poll_table"]')

        tbody = elements.first.find_by_tag('tbody')
        tr = tbody.find_by_tag('tr').first
        tds = tr.find_by_tag('td')
        total = 0
        for td in tds[1:]:
            total += int(td.value.split(' ')[0])
        self.assertEquals(responses.count(), total)

    def assert_that_poll_end_date_is_none(self, poll):
        assert poll.end_date is None

    def assert_that_page_has_add_poll_button(self):
        self.assertTrue(self.browser.find_link_by_href('/createpoll/'))

    def assert_that_page_has_edit_poll_button(self, poll):
        element = self.browser.find_link_by_href('/view_poll/%i/' % poll.id)

        self.assertEqual(element.first.text, "Edit")