from django.http import Http404
import django.utils.simplejson as json
import unittest

from django.test import RequestFactory
from mock import Mock

from ureport.views.api.ViewUreporter import ViewUreporter


class ViewUreporterTest(unittest.TestCase):
    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        fake_request = request_factory.get('/')
        return view.get(fake_request, None, **kwargs)

    def test_is_called_with_backend_and_address(self):
        view = ViewUreporter()
        kwargs = {"backend": "console", "user_address": "999"}
        self.get_http_response_from_view(kwargs, view)
        self.assertEqual("console", view.backend_name)
        self.assertEqual("999", view.user_address)

    def test_if_the_request_is_valid(self):
        view = ViewUreporter()
        kwargs = {"backend": "console", "user_address": "999"}
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertEqual(True, data['success'])

    def test_that_in_case_of_post_it_raise_404(self):
        view = ViewUreporter()
        with self.assertRaises(Http404):
            http_response = view.post(None)

    def test_that_return_not_registered_if_contact_does_not_exist(self):
        view = ViewUreporter()
        fake_check = Mock()
        fake_check.return_value = {"id": "", "language": "", "registered": False}
        view.get_contact = fake_check
        kwargs = {"backend": "console", "user_address": "999"}
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertEqual(False, data['user']['registered'])

    def test_that_return_registered_true_if_contact_exists(self):
        view = ViewUreporter()
        fake_check = Mock()
        fake_check.return_value = {"id": 12, "language": "en", "registered": True}
        view.get_contact = fake_check
        kwargs = {"backend": "console", "user_address": "999"}
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertEqual(True, data['user']['registered'])
        self.assertEqual(12, data['user']['id'])
        self.assertEqual('en', data['user']['language'])
