from django.http import Http404
import django.utils.simplejson as json
import unittest

from django.test import RequestFactory
from mock import Mock

from ureport.views.api.ViewUReporter import ViewUReporter


class ViewUreporterTest(unittest.TestCase):
    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        fake_request = request_factory.get('/')
        return view.get(fake_request, None, **kwargs)



    def test_that_in_case_of_post_it_raise_404(self):
        view = ViewUReporter()
        with self.assertRaises(Http404):
            http_response = view.post(None)

    def test_that_return_not_registered_if_contact_does_not_exist(self):
        view = ViewUReporter()
        fake_check = Mock()
        fake_check.return_value = {"id": "", "language": "", "registered": False}
        view.get_contact = fake_check
        kwargs = {"backend": "console", "user_address": "999"}
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertDictEqual({"success":False,"reason":"Ureporter not found"}, data)

    def test_that_return_registered_true_if_contact_exists(self):
        view = ViewUReporter()
        fake_check = Mock()
        fake_check.return_value = {"id": 12, "language": "en", "registered": True}
        view.get_contact = fake_check
        kwargs = {"backend": "console", "user_address": "999"}
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertEqual(True, data['success'])
        self.assertEqual(True, data['user']['registered'])
        self.assertEqual('en', data['user']['language'])
