from splinter_wrapper import SplinterTestCase
from ureport.tests.functional.admin_helper import fill_form_and_submit, fill_form
from datetime import datetime
import time
from ureport.tests.functional.constants import WAIT_TIME_IN_SECONDS

REPORTING_LOCATION_ID_KAMAIBA = "Kamaiba"
REPORTING_LOCATION_KAMAIBA_DISTRICT = "Kasese"

class AdminBase (SplinterTestCase):
    def create_backend(self, name):
        self.open("/admin/rapidsms/backend/add/")
        fill_form_and_submit(self.browser, {"id_name": name}, "_save")

    def create_contact(self, name, gender, backend_name, identity, group):
        self.open("/admin/rapidsms/contact/add/")
        time.sleep(WAIT_TIME_IN_SECONDS)
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
        fill_form_and_submit(self.browser, form_data, "_save")

    def create_group(self, name):
        self.open("/admin/auth/group/add/")
        time.sleep(WAIT_TIME_IN_SECONDS)
        fill_form_and_submit(self.browser, {"id_name": name}, "_save")

    def create_user(self, name, group):
        self.open("/admin/auth/user/add/")
        time.sleep(WAIT_TIME_IN_SECONDS)
        fill_form_and_submit(self.browser, {"id_username": name, "id_password1": name, "id_password2": name}, "_save")
        fill_form_and_submit(self.browser, {"id_groups": group}, "_save")

    def change_users_group(self, name):
        self.open("/admin/auth/user")
        time.sleep(WAIT_TIME_IN_SECONDS)
        self.browser.click_link_by_text("ureport")
        time.sleep(WAIT_TIME_IN_SECONDS)
        fill_form_and_submit(self.browser, {"id_groups": name}, "_save")

    def log_in_as_ureport(self):
        self.open('/accounts/login')
        self.browser.fill("username", "ureport")
        self.browser.fill("password", "ureport")
        self.browser.find_by_css("input[type=submit]").first.click()

    def log_as_admin_and_visit(self, url):
        self.create_and_sign_in_admin("ureport", "ureport", url)

    def cleanup(self, url):
        self.open(url)
        if self.browser.is_element_present_by_id("action-toggle"):
            fill_form(self.browser, {"action-toggle": True})
            fill_form_and_submit(self.browser, {"action": "delete_selected"}, "index", True, True)
            self.browser.find_by_value("Yes, I'm sure").first.click()