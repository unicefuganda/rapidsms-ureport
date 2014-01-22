import unittest
from ureport.tests.functional.admin_helper import fill_form
from ureport.tests.functional.splinter_wrapper import SplinterWrapper


class AuthenticationTest(unittest.TestCase):
    browser = SplinterWrapper.getBrowser()

    def test_login_redirects_to_admin_dashboard_on_success(self):
        SplinterWrapper.open("/accounts/login")
        fill_form(self.browser, {"username": "ureport", "password":"ureport"}, True, True)
        self.browser.find_by_value("login").first.click()

        self.assertEqual(self.browser.is_text_present('Add New Poll'), True)