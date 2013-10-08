from datetime import datetime
from django.conf import settings
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form
from ureport.tests.functional.splinter_wrapper import SplinterWrapper

REPORTING_LOCATION_ID_KAMAIBA = "Kamaiba"
REPORTING_LOCATION_KAMAIBA_DISTRICT = "Kasese"

class AdminBase():
    browser = SplinterWrapper.getBrowser()

    @classmethod
    def create_backend(cls, browser, name):
        SplinterWrapper.open("/admin/rapidsms/backend/add/")
        fill_form_and_submit(browser, {"id_name": name}, "_save")

    @classmethod
    def create_contact(cls, browser, name, gender, backend_name, identity, group):
        SplinterWrapper.open("/admin/rapidsms/contact/add/")
        form_data = {
            "id_name": name,
            "id_gender": gender,
            "id_birthdate_0": datetime.now().strftime("%Y-%m-%d"),
            "id_birthdate_1": "00:00:00",
            "id_reporting_location": ("%s" % REPORTING_LOCATION_ID_KAMAIBA),
            "id_connection_set-0-backend": backend_name,
            "id_connection_set-0-identity": identity,
            "id_groups": group
        }
        fill_form_and_submit(browser, form_data, "_save")

    @classmethod
    def create_group(cls, browser, name):
        SplinterWrapper.open("/admin/auth/group/add/")
        fill_form_and_submit(browser, {"id_name": name}, "_save")

    def create_user(self, name, group):
        SplinterWrapper.open("/admin/auth/user/add/")
        fill_form_and_submit(self.browser, {"id_username": name, "id_password1": name, "id_password2": name}, "_save")
        fill_form_and_submit(self.browser, {"id_groups": group}, "_save")

    @classmethod
    def change_users_group(cls, group_name):
        SplinterWrapper.open("/admin/auth/user")
        cls.browser.click_link_by_text("ureport")
        fill_form_and_submit(cls.browser, {"id_groups": group_name}, "_save")

    @classmethod
    def log_in_as_ureport(cls):
        SplinterWrapper.open('/accounts/login')
        cls.browser.fill("username", "ureport")
        cls.browser.fill("password", "ureport")
        cls.browser.find_by_css("input[type=submit]").first.click()

    def log_as_admin_and_visit(self, url):
        self.create_and_sign_in_admin("ureport", "ureport", url)

    def cleanup(self, url):
        self.open(url)
        if self.browser.is_element_present_by_id("action-toggle"):
            fill_form(self.browser, {"action-toggle": True})
            fill_form_and_submit(self.browser, {"action": "delete_selected"}, "index", True, True)
            self.browser.find_by_value("Yes, I'm sure").first.click()