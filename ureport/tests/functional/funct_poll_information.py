from splinter import Browser
from ureport.tests.functional.admin_base import AdminBase
from ureport.tests.functional.poll_base import PollBase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form


class PollInformationTest(PollBase, AdminBase):

    def setUp(self):
        self.browser = Browser()
        self.log_in_as_ureport()

    def cleanup(self, url):
        self.open(url)

        if self.browser.is_element_present_by_id("action-toggle"):
            fill_form(self.browser, {"action-toggle": True})
            fill_form_and_submit(self.browser, {"action": "delete_selected"}, "index", True, True)
            self.browser.find_by_value("Yes, I'm sure").first.click()

    def tearDown(self):

        self.cleanup("/admin/poll/poll/")
        self.cleanup("/admin/rapidsms/connection/")
        self.cleanup("/admin/rapidsms/backend/")
        self.cleanup("/admin/rapidsms/contact/")
        self.cleanup("/admin/auth/group/")
        #TODO: when deleting users don't delete the "ureport" and "admin" ones
        # self.cleanup("/admin/auth/user/")

        self.browser.quit()

    def test_that_admin_is_able_to_edit_a_poll(self):
        self.create_group("groupFT")
        self.create_backend("console")
        self.create_contact("FT1", "Male", "console", "0794339344", "groupFT")
        self.create_contact("FT2", "Female", "console", "0794339345", "groupFT")

        poll_id = self.create_poll("Some poll", "Yes/No Question", "What is your name", "groupFT")

        self.start_poll(poll_id)
        self.respond_to_the_started_poll("0794339344", "yes")

        self.open("/mypolls/%s/" % poll_id)
        self.assert_that_page_has_edit_poll_option(poll_id)
        #TODO edit the poll

    def test_that_admin_can_check_poll_report_option(self):
        self.create_group("groupFT")
        self.create_backend("console")
        self.create_contact("FT1", "Male", "console", "0794339344", "groupFT")
        self.create_contact("FT2", "Female", "console", "0794339345", "groupFT")

        poll_id = self.create_poll("Some poll", "Yes/No Question", "What is your name", "groupFT")
        self.start_poll(poll_id)
        self.respond_to_the_started_poll("0794339344", "yes")
        self.open("/mypolls/%s/" % poll_id)
        self.assert_that_page_has_report_poll_option(poll_id)
