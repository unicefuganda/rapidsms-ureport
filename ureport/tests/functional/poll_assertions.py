from ureport.tests.functional.splinter_wrapper import SplinterWrapper
from datetime import date
from ureport.tests.functional.admin_helper import rows_of_table_by_class
import time


from ureport.tests.functional.test_data import WAIT_TIME_IN_SECONDS

ANY_POLL_ID = '12'



class PollAssertions(SplinterWrapper):
    def assert_that_poll_start_date_is_not_none(self, poll_id):
        SplinterWrapper.open(self.browser,'/mypolls/%s' % poll_id)
        start_date = self.browser.find_by_xpath('//*[@class="results"]/tbody/tr[2]/td[3]')
        date_today = date.today().strftime("%d/%m/%Y")
        self.assertEquals(start_date.text, date_today)

    def assert_that_poll_has_responses(self, poll):
        self.assertEquals(poll.responses.count(), 2)
        elements = self.browser.find_link_by_href('/%i/responses/' % poll.id)
        assert elements.first.value == 'Responses (%i)' % poll.responses.count()

    def assert_that_question_is(self, question):
        time.sleep(WAIT_TIME_IN_SECONDS)
        elements = self.browser.find_by_xpath('//*[@class="question"]')
        assert elements.first.value == question

    def assert_the_number_of_participants_of_the_poll_is(self, responses_count):
        elements = self.browser.find_by_xpath('//*[@class="participants"]')
        num_participants = elements.first.value.split(' ')[0]
        self.assertEquals(int(num_participants), responses_count)

    def assert_that_response_location_is(self, location):
        elements = self.browser.find_by_xpath('//*[@class="poll_table"]')
        tbody = elements.find_by_tag('tbody')
        trs = tbody.find_by_tag('tr')
        tds = trs.find_by_tag('td')

        self.assertEquals(tds.first.value, location)

    def assert_that_number_of_responses_is(self,responses_count):
        elements = self.browser.find_by_xpath('//*[@class="poll_table"]')
        tbody = elements.first.find_by_tag('tbody')
        tr = tbody.find_by_tag('tr').first
        tds = tr.find_by_tag('td')
        total = 0
        for td in tds[1:]:
            total += int(td.value.split(' ')[0])
        self.assertEquals(responses_count, total)

    def assert_that_poll_end_date_is_none(self, poll_id):
        SplinterWrapper.open(self.browser,'/mypolls/%s' % poll_id)

        elements = self.browser.find_by_xpath('//*[@class="results"]')
        tbody = elements.first.find_by_tag('tbody')
        trs = tbody.find_by_tag('tr')
        view_poll_link = '/view_poll/%s/' % poll_id
        for tr in trs:
            element = tr.find_by_xpath('//*[@href="%s"]' % view_poll_link).first
            if element is not None:
                start_date = date.today().strftime("%d/%m/%Y")
                self.assertTrue(tr.find_by_value(start_date) is not None)

    def assert_that_page_has_add_poll_button(self):
        self.assertTrue(self.browser.find_link_by_href('/createpoll/'))

    def assert_that_page_has_edit_poll_option(self, poll):
        element = self.browser.find_link_by_href('/view_poll/%i/' % poll.id)

        self.assertEqual(element.first.text, "Edit")

    def assert_that_page_has_report_poll_option(self, poll):
        element = self.browser.find_link_by_href('/polls/%i/report/' % poll.id)

        self.assertEqual(element.first.text, "Report")

    def assert_that_poll_question_are_sent_out_to_contacts(self, number_of_contact_for_poll, question):
        SplinterWrapper.open(self.browser,'/router/console')
        rows = rows_of_table_by_class(self.browser, 'messages module')
        total = 0
        for row in rows:
            if row.find_by_tag('td').first.text == question:
                total += 1
        self.assertEqual(total, number_of_contact_for_poll)

    def assert_that_number_of_responses_increase_by(self, number_of_responses, increment):
        SplinterWrapper.open(self.browser,'/router/console')
        rows_responses = rows_of_table_by_class(self.browser, "messages module")
        self.assertEqual(len(rows_responses), number_of_responses + increment)

    def assert_that_message_has_been_sent_out_to_ureporter(self, message):
        SplinterWrapper.open(self.browser, "/router/console")
        element =self.browser.find_by_xpath("//table/tbody/tr/td[text()='%s']" % message)
        self.assertEquals(element.first.text, message)