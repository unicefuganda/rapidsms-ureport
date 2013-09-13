from splinter_wrapper import SplinterTestCase
from ureport.tests.functional.admin_helper import fill_form_and_submit
from datetime import datetime

class AdminBase (SplinterTestCase):
    def create_backend(self, name):
        self.open("/admin/rapidsms/backend/add/")
        fill_form_and_submit(self.browser, {"id_name": name}, "_save")

    def create_contact(self, name, gender, backend_name, identity, group):
        self.open("/admin/rapidsms/contact/add/")
        form_data = {
            "id_name": name,
            "id_gender": gender,
            "id_birthdate_0": datetime.now().strftime("%Y-%m-%d"),
            "id_birthdate_1": "00:00:00",
            "id_connection_set-0-backend": backend_name,
            "id_connection_set-0-identity": identity,
            "id_groups": group
        }
        fill_form_and_submit(self.browser, form_data, "_save")

    def create_group(self, name):
        self.open("/admin/auth/group/add/")
        fill_form_and_submit(self.browser, {"id_name": name}, "_save")

    def create_user(self, name, group):
        self.open("/admin/auth/user/add/")
        fill_form_and_submit(self.browser, {"id_username": name, "id_password1": name, "id_password2": name}, "_save")
        fill_form_and_submit(self.browser, {"id_groups": group}, "_save")
