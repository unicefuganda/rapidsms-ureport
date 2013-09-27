import time

from splinter import Browser
from ureport.tests.functional.admin_helper import fill_form_and_submit
from ureport.tests.functional.constants import WAIT_TIME_IN_SECONDS

from ureport.tests.functional.poll_base import PollBase


class ManageUreporterBase(PollBase):
    def given_a_male_ureporter_with_the_name(self, name):
        console = "console"
        self.create_group("%s" % self.group_name)
        self.create_backend(console)
        self.create_contact(name, "Male", console, self.contact_identity, self.group_name)
        self.open("/admin/rapidsms/connection/")
        self.browser.click_link_by_partial_text(self.contact_identity)
        self.ureporter_id = self.browser.url.split('/')[-2]
        return self

    def when_the_admin_goes_to_the_ureporters_page(self):
        self.open('/reporter/')
        return self


    def when_the_admin_searches_for_the_id(self, id):
        self.browser.fill("searchx", id)
        self.browser.click_link_by_partial_text("Update")
        time.sleep(WAIT_TIME_IN_SECONDS)
        return self

    def then_the_admin_should_not_see_the_ureporters_id(self, text):
        assert not self.browser.is_text_present(text)
        return self

    def then_the_admin_should_see_the_ureporters_id(self, text):
        assert self.browser.is_text_present(text)
        return self


    def and_the_admin_has_started_a_poll(self):
        question = "hello it is me you are looking for ?"
        poll_id = self.create_poll(question, "Yes/No Question", question, self.group_name)
        self.start_poll(poll_id)
        return self


    def and_the_ureporter_responds_to_the_poll(self):
        self.respond_to_the_started_poll(self.contact_identity, "No")
        return self


    def and_the_admin_is_part_of_the_group(self, name):
        self.open('/admin/auth/user/')
        self.browser.click_link_by_text('ureport')
        fill_form_and_submit(self.browser, {"id_groups": name}, "_save")
        return self


class ManageUreporterTest(ManageUreporterBase):
    def setUp(self):
        self.browser = Browser()
        self.log_in_as_ureport()
        self.group_name = "groupFT"
        self.contact_identity = "4444"
        self.ureporter_name = "U1"

    def tearDown(self):
        self.cleanup("/admin/poll/poll/")
        self.cleanup("/admin/rapidsms/connection/")
        self.cleanup("/admin/rapidsms/backend/")
        self.cleanup("/admin/rapidsms/contact/")
        self.cleanup("/admin/auth/group/")
        self.browser.quit()

    def test_admin_can_search_for_ureporter(self):
        self.given_a_male_ureporter_with_the_name(self.ureporter_name) \
            .and_the_admin_has_started_a_poll() \
            .and_the_ureporter_responds_to_the_poll() \
            .and_the_admin_is_part_of_the_group(self.group_name) \
            .when_the_admin_goes_to_the_ureporters_page() \
            .then_the_admin_should_see_the_ureporters_id(self.ureporter_id) \
            .when_the_admin_searches_for_the_id("999999999") \
            .then_the_admin_should_not_see_the_ureporters_id(self.ureporter_id) \
            .when_the_admin_searches_for_the_id(self.ureporter_id) \
            .then_the_admin_should_see_the_ureporters_id(self.ureporter_id) \



