from ureport.tests.functional.splinter_wrapper import SplinterTestCase
from ureport.tests.functional.admin_helper import rows_of_table_by_class
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure

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

    def assert_that_page_has_edit_poll_option(self, poll_id):
        element = self.browser.find_link_by_href('/view_poll/%s/' % poll_id)

        self.assertEqual(element.first.text, "Edit")

    @take_screenshot_on_failure
    def assert_that_page_has_report_poll_option(self, poll_id):
        element = self.browser.find_link_by_href('/polls/%s/report/' % poll_id)

        self.assertEqual(element.first.text, "Report")

    def assert_create_poll_is_present(self):
        is_create_poll_present = self.browser.is_element_present_by_css(".buttons a")
        self.assertTrue(is_create_poll_present)

    def assert_that_number_of_responses_increase_by_one(self, number_of_responses):
        rows_responses = rows_of_table_by_class(self.browser, "messages module")
        self.assertEqual(len(rows_responses), number_of_responses + 1)
