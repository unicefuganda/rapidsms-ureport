from django.http import Http404
import django.utils.simplejson as json
import unittest

from django.test import RequestFactory
from mock import Mock
from rapidsms.models import Backend, Connection
from ureport.views.api.view_ureporter import ViewUReporter


class ViewUreporterTest(unittest.TestCase):
    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        fake_request = request_factory.get('/')
        return view.dispatch(fake_request, None, **kwargs)

    def test_404_is_raised_if_backend_does_not_exist(self):
        view = ViewUReporter()
        with self.assertRaises(Http404):
            response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, view)

    def test_that_in_case_of_post_it_raise_405(self):
        view = ViewUReporter()
        http_response = view.post(None)
        self.assertEqual(405, http_response.status_code)

    def test_that_return_not_registered_if_contact_does_not_exist(self):
        view = ViewUReporter()
        fake_check = Mock()
        fake_check.return_value = {"id": "", "language": "", "registered": False}
        view.get_contact = fake_check
        kwargs = {"backend": "console", "user_address": "999"}
        view.get_backend = Mock(return_value=Backend(name="my_backend"))
        view.get_connection = Mock(return_value=Connection(identity="999"))
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertDictEqual({"success": False, "reason": "Ureporter not found"}, data)

    def test_that_return_registered_true_if_contact_exists(self):
        view = ViewUReporter()
        fake_check = Mock()
        fake_check.return_value = {"id": 12, "language": "en", "registered": True}
        view.get_contact = fake_check
        kwargs = {"backend": "console", "user_address": "999"}
        view.get_backend = Mock(return_value=Backend(name="my_backend"))
        view.get_connection = Mock(return_value=Connection(identity="999"))
        http_response = self.get_http_response_from_view(kwargs, view)
        json_string = http_response.content
        data = json.loads(json_string)
        self.assertEqual(True, data['success'])
        self.assertEqual(True, data['user']['registered'])
        self.assertEqual('en', data['user']['language'])
