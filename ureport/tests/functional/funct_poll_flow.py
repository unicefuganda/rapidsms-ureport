from datetime import datetime
from splinter import Browser
from ureport.tests.functional.take_screenshot import take_screenshot_on_failure
from ureport.tests.functional.poll_base import PollBase


class PollFlowTest(PollBase):
    def fill_form(self, field_values, by_name=False, select_by_value=False):
        for id, value in field_values.items():
            if by_name:
                elements = self.browser.find_by_name(id)
            else:
                elements = self.browser.find_by_id(id)
            element = elements.first
            if element['type'] == 'text' or element.tag_name == 'textarea' or element['type'] == 'password':
                element.value = value
            elif element['type'] == 'checkbox':
                if value:
                    element.check()
                else:
                    element.uncheck()
            elif element['type'] == 'radio':
                for field in elements:
                    if field.value == value:
                        field.click()
            elif element._element.tag_name == 'select':
                if select_by_value:
                    element.find_by_value(value).first._element.click()
                else:
                    element.find_by_xpath('.//*[contains(., "%s")]' % value).first._element.click()

    def fill_form_and_submit(self, form_data, submit_button_name, by_name=False, select_by_value=False):
        self.fill_form(form_data, by_name, select_by_value)
        self.browser.find_by_name(submit_button_name).first.click()

    def create_backend(self, name):
        self.open("/admin/rapidsms/backend/add/")
        if not self.browser.html:
            print "$$$$$$$$$$$"
            print "$$$$$ OMG OMG NO HTML!!!!!!!!"
            print "$$$$$$$$$$$"
        #self.browser.find_by_tag('body').first.click()
        self.fill_form_and_submit({"id_name": name}, "_save")

    def create_contact(self, name, gender, backend_name, identity, group):
        self.open("/admin/rapidsms/contact/add/")
        if not self.browser.html:
            print "$$$$$$$$$$$"
            print "$$$$$ OMG OMG NO HTML!!!!!!!!"
            print "$$$$$$$$$$$"
        #self.browser.find_by_tag('body').first.click()
        form_data = {
            "id_name": name,
            "id_gender": gender,
            "id_birthdate_0": datetime.now().strftime("%Y-%m-%d"),
            "id_birthdate_1": "00:00:00",
            "id_connection_set-0-backend": backend_name,
            "id_connection_set-0-identity": identity,
            "id_groups": group
        }
        self.fill_form_and_submit(form_data, "_save")

    def create_group(self, name):
        self.open("/admin/auth/group/add/")
        if not self.browser.html:
            print "$$$$$$$$$$$"
            print "$$$$$ OMG OMG NO HTML!!!!!!!!"
            print "$$$$$$$$$$$"
        #self.browser.find_by_tag('body').first.click()
        self.fill_form_and_submit({"id_name": name}, "_save")

    def create_user(self, name, group):
        self.open("/admin/auth/user/add/")
        #self.browser.find_by_tag('body').first.click()
        self.fill_form_and_submit({"id_username": name, "id_password1": name, "id_password2": name}, "_save")
        self.fill_form_and_submit({"id_groups": group}, "_save")

    def create_poll(self, name, type, question, group):
        self.open("/createpoll")
        #self.browser.find_by_tag('body').first.click()
        form_data = {
            "id_type": type,
            "id_name": name,
            "id_groups": group
        }
        self.browser.fill("question_en", question)
        self.fill_form(form_data)
        self.browser.find_by_css(".buttons a").last.click()
        return self.browser.url.split('/')[-2]

    @take_screenshot_on_failure
    def setUp(self):
        self.browser = Browser()
        self.log_in_as_ureport()

    def cleanup(self, url):
        self.open(url)
        
        if self.browser.is_element_present_by_id("action-toggle"):
            self.fill_form({"action-toggle": True})
            self.fill_form_and_submit({"action": "delete_selected"}, "index", True, True)
            self.browser.find_by_value("Yes, I'm sure").first.click()

    @take_screenshot_on_failure
    def tearDown(self):

        self.cleanup("/admin/poll/poll/")
        self.cleanup("/admin/rapidsms/connection/")
        self.cleanup("/admin/rapidsms/backend/")
        self.cleanup("/admin/rapidsms/contact/")
        self.cleanup("/admin/auth/group/")
        #TODO: when deleting users don't delete the "ureport" and "admin" ones
        # self.cleanup("/admin/auth/user/")

        self.browser.quit()

    # def test_that_poll_status_changes_when_started(self):
    #     self.start_poll_through_poll_page()
    #
    #     assert self.browser.is_text_present('Close Poll')
    #     self.assert_that_poll_start_date_is_not_none(self.get_poll(self.poll.id))

    # def test_that_poll_can_be_sent_out_to_contacts(self):
    #     self.start_poll()
    #     newly_added_poll = self.get_poll(self.poll.id)
    #
    #     self.assert_that_poll_questions_are_sent_out_to_contacts(poll=newly_added_poll)
    #
    # def test_that_polls_can_be_responded(self):
    #     self.start_poll()
    #     newly_added_poll = self.get_poll(self.poll.id)
    #
    #     self.respond_to_poll(newly_added_poll)
    #     self.log_as_admin_and_visit('/mypolls/%s' % self.poll.id)
    #
    #     self.assert_that_poll_has_responses(newly_added_poll)
    #
    # def test_that_polls_can_be_reopen(self):
    #     self.close_poll()
    #     self.log_as_admin_and_visit("/view_poll/%s" % self.poll.id)
    #
    #     self.browser.find_link_by_text('Reopen Poll').first.click()
    #     self.assert_that_poll_end_date_is_none(self.get_poll(self.poll.id))
    #
    # def test_that_admin_is_able_to_add_new_poll(self):
    #     self.log_as_admin_and_visit('/mypolls/%s' % self.poll.id)
    #
    #     self.assert_that_page_has_add_poll_button()

    @take_screenshot_on_failure
    def test_should_show_the_status_page(self):
        self.create_group("groupFT")
        self.create_backend("Some backend")
        self.create_contact("FT1", "Male", "Some backend", "0794339344", "groupFT")
        self.create_contact("FT2", "Male", "Some backend", "0794339344", "groupFT")

        poll_id = self.create_poll("Some poll", "Yes/No Question", "What is your name", "groupFT")

        self.open("/poll_status/%s" % poll_id)

        self.assertEqual(self.browser.is_element_present_by_id('poll-details'), True)
        self.assertTrue(poll_id in self.browser.find_by_id("poll-details").first.text)

        self.assertEqual(self.browser.find_by_id('contact-count').text, "2")
        self.assertEqual(self.browser.find_by_id('category-count').text, "3")
        self.assertEqual(self.browser.find_by_id('is-yesno').text, "yes")
