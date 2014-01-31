import base64
from unittest import TestCase
from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory
from mock import Mock
from ureport.views.api.base import BasicAuthenticationView


class DummyView(BasicAuthenticationView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("")


class BasicAuthenticationViewTest(TestCase):
    def setUp(self):
        self.view = DummyView()
        self.request_factory = RequestFactory()

    def test_that_if_there_are_no_auth_headers_a_401_is_returned(self):
        fake_request = self.request_factory.get("/")
        response = self.view.dispatch(fake_request)
        self.assertEqual(401, response.status_code)


    def test_that_if_the_username_and_password_are_not_sent_you_get_a_401_response_code(self):
        fake_request = self.request_factory.get("/", **{"HTTP_AUTHORIZATION": ""})
        response = self.view.dispatch(fake_request)
        self.assertEqual(401, response.status_code)

    def test_that_if_the_username_and_password_are_sent_and_are_invalid_you_get_a_401_response_code(self):
        auth_string = base64.b64encode("who:why")
        fake_request = self.request_factory.get("/", **{"HTTP_AUTHORIZATION": ("Basic %s" % auth_string)})
        self.view.validate_credentials = Mock(return_value=False)
        response = self.view.dispatch(fake_request)
        self.assertEqual(401, response.status_code)

    def test_that_if_the_username_and_password_are_sent_and_valid_you_get_a_200_response_code(self):
        auth_string = base64.b64encode("who:why")
        fake_request = self.request_factory.get("/", **{"HTTP_AUTHORIZATION": ("Basic %s" % auth_string)})
        self.view.validate_credentials = Mock(return_value=True)
        response = self.view.dispatch(fake_request)
        self.assertEqual(200, response.status_code)

    def test_that_if_correct_username_and_password_are_available_in_the_api_user_setting_they_are_validated(self):
        settings.API_USERS = {"test": "secret"}
        self.assertEqual(True, self.view.validate_credentials("test", "secret"))


    def test_that_if_correct_username_and_password_are__not_available_in_the_api_user_setting_they_are_not_validated(
            self):
        settings.API_USERS = {}
        self.assertEqual(False, self.view.validate_credentials("test2", "secret2"))