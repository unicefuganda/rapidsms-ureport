import time

from poll.models import Poll
from ureport.tests.functional.splinter_wrapper import SplinterWrapper
from ureport.tests.functional.admin_helper import fill_form
from ureport.tests.functional.poll_assertions import PollAssertions
from ureport.tests.functional.admin_helper import rows_of_table_by_class
from ureport.tests.functional.admin_base import AdminBase


class PollBase(PollAssertions):
    browser = SplinterWrapper.getBrowser()

    @classmethod
    def start_poll(cls,browser, poll_id):
        SplinterWrapper.open("/view_poll/%s " % poll_id)

        browser.find_link_by_text('Start Poll').first.click()
        time.sleep(2) #Sending questions is an asynchronous process

    @classmethod
    def reopen_poll(cls,browser, poll_id):
        SplinterWrapper.open("/view_poll/%s " % poll_id)
        browser.find_link_by_text('Reopen Poll').first.click()
    @classmethod
    def close_poll(cls, poll_id):
        SplinterWrapper.open("/view_poll/%s" % poll_id)
        cls.browser.find_link_by_text('Close Poll').first.click()


    def get_poll(self, poll_id):
        return Poll.objects.get(id=poll_id)

    @classmethod
    def respond_to_the_started_poll(cls, sender, message):
        SplinterWrapper.open('/router/console/')
        rows_responses = rows_of_table_by_class(cls.browser, "messages module")
        number_of_responses = len(rows_responses)

        form_data = {
            "text": message,
            "sender": sender
        }
        fill_form(cls.browser, form_data, True)
        cls.browser.find_by_css("input[type=submit]").first.click()
        return number_of_responses

    def get_poll_response_location(self, response):
        contact = response.message.connection.contact
        location = contact.reporting_location
        return location.name

    def get_first_poll_response_location(self, poll):
        responses = self.get_poll_responses(poll)
        return self.get_poll_response_location(responses[0])

    def get_poll_responses(self, poll):
        responses = poll.responses.all()
        return responses

    @classmethod
    def create_poll(cls, browser, name, type, question, group):
        SplinterWrapper.open("/createpoll/")
        form_data = {
            "id_type": type,
            "id_name": name,
            "id_groups": group
        }
        browser.fill("question_en", question)
        fill_form(browser, form_data)
        browser.find_by_css(".buttons a").last.click()

        return browser.url.split('/')[-2]

    @classmethod
    def setup_poll(cls,browser, question="What is your name", number_prefix="079433934"):
        AdminBase.create_group(browser,"groupFT")
        AdminBase.create_backend(browser,"console")
        AdminBase.create_contact(browser,"FT1", "Male", "console", "%s4" % number_prefix, "groupFT")
        poll_id = PollBase.create_poll(browser,question, "Yes/No Question", question, "groupFT")

        return poll_id, question

    @classmethod
    def reassign_poll_response(cls, poll_id, second_poll_id):
        SplinterWrapper.open("/%s/responses/" % poll_id)
        responses_all = cls.browser.find_by_id("input_select_all").first
        responses_all.check()
        elements = cls.browser.find_by_id("id_poll")
        elements.first.find_by_value(second_poll_id).first._element.click()
        assign_link = cls.browser.find_link_by_text("Assign selected to poll")
        assign_link.click()

    @classmethod
    def reply_poll_to_an_ureporter(cls, poll_id, message):
        SplinterWrapper.open("/%s/responses/" % poll_id)
        responses_all = cls.browser.find_by_id("input_select_all").first
        responses_all.check()
        cls.browser.fill("text", message)
        reply_link = cls.browser.find_link_by_text("Reply to selected")
        reply_link.click()








