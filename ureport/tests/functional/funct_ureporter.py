from splinter_wrapper import SplinterWrapper
from ureport.tests.functional.admin_base import AdminBase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form

from ureport.tests.functional.poll_base import PollBase

class TestManageUreporter(PollBase):
    browser = SplinterWrapper.getBrowser()


    group_name = "groupFT"
    contact_identity = "4444"
    ureporter_name = "U1"

    @classmethod
    def setUpClass(cls):
        AdminBase.log_in_as_ureport(cls.browser)


    @classmethod
    def cleanup(cls, url):
        SplinterWrapper.open(cls.browser,url)

        if cls.browser.is_element_present_by_id("action-toggle"):
            fill_form(cls.browser, {"action-toggle": True})
            fill_form_and_submit(cls.browser, {"action": "delete_selected"}, "index", True, True)
            cls.browser.find_by_value("Yes, I'm sure").first.click()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup("/admin/poll/poll/")
        cls.cleanup("/admin/poll/response/")
        cls.cleanup("/admin/rapidsms/connection/")
        cls.cleanup("/admin/rapidsms/backend/")
        cls.cleanup("/admin/rapidsms/contact/")
        cls.cleanup("/admin/auth/group/")
        SplinterWrapper.open(cls.browser, '/account/logout')
        cls.browser.quit()


    def search_by_ureporter_group(self, group_name):
        element_list_macthing_option = self.browser.find_option_by_text(group_name)
        self.browser.select("groups", element_list_macthing_option.first.value)
        self.browser.click_link_by_partial_text("Update")
        return self


    def test_admin_can_search_for_ureporter(self):
        poll_id, question = PollBase.setup_poll(self.browser,"Are you happy today?",number_prefix="0793449")
        PollBase.start_poll(self.browser,poll_id)
        self.respond_to_the_started_poll("07934494", "No")
        group_name = "groupFT"
        self.change_users_group(group_name)
        SplinterWrapper.open(self.browser, '/reporter/')
        self.search_by_ureporter_group("%s" % group_name)
        self.assertEquals(True, self.browser.is_text_present("07934494"))
    #
    # def test_admin_can_filter_by_group(self):
    #     self.given_a_male_ureporter_with_the_name(self.ureporter_name) \
    #         .and_the_admin_has_started_a_poll() \
    #         .and_the_ureporter_responds_to_the_poll() \
    #         .and_the_admin_is_part_of_the_group(self.group_name) \
    #         .when_the_admin_goes_to_the_ureporters_page() \
    #         .and_filters_by_the_group(self.group_name) \
    #         .then_the_admin_should_see_the_ureporters_id(self.ureporter_id)
    #
    #
    #


