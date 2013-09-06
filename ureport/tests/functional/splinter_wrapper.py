import datetime
from django.contrib.auth.models import User
from django.test import TransactionTestCase
import settings


class SplinterTestCase(TransactionTestCase):
    def __init__(self, methodName='runTest'):
        super(SplinterTestCase, self).__init__(methodName)

    def follow_link(self, text):
        (self.browser.find_element_by_link_text(text)).click()

    def select_by_text(self, name, text):
        self.browser.find_by_xpath(
            '//select[@name="%s"]/option[normalize-space(.)="%s"]' % (name, text)).first._element.click()

    def create_and_sign_in_admin(self, username, password, redirect_to):
        User.objects.create_superuser(username, 'admin@test.com', password)

        url = '/accounts/login'
        if redirect_to:
            url = "%s?next=%s" % (url, redirect_to)

        self.open(url)
        self.browser.fill("username", username)
        self.browser.fill("password", password)
        self.browser.find_by_css("input[type=submit]").first.click()

    def open(self, url):
        self.browser.visit("%s%s" % (settings.TEST_SERVER_URL, url))

    def wait_for_seconds(self, time_out_in_seconds):
        current_time = datetime.datetime.now()
        end_time = current_time + datetime.timedelta(0, time_out_in_seconds)

        while current_time < end_time:
            current_time = datetime.datetime.now()
