import json
import unittest
from django.http import Http404
from django.test import RequestFactory
from mock import Mock
from rapidsms.models import Backend, Connection
from ureport.tests.functional.views.api.helpers import TestBasicAuthMixin
from ureport.views.api.submit_report import SubmitReportApiView


class SubmitReportTestCase(unittest.TestCase, TestBasicAuthMixin):
    def setUp(self):
        self.view = SubmitReportApiView()
        self.request_factory = RequestFactory()

    def test_that_in_case_of_get_it_raise_405(self):
        http_response = self.view.get(None)
        self.assertEqual(405, http_response.status_code)

    def test_that_if_the_user_address_does_not_exist_you_get_a_404(self):
        backend = Backend(id=89)
        connection = Connection(identity=999, backend=backend)
        fake_request = self.setup_post_request(backend, connection)
        with self.assertRaises(Http404):
            response = self.view.dispatch(fake_request)
            print response.status_code

    def setup_post_request(self, backend, connection):
        self.view.get_backend = Mock(return_value=backend)
        self.view.get_connection = Mock(return_value=connection)
        self.view.validate_credentials = Mock(return_value=True)
        fake_request = self.request_factory.post("/", **{"backend": "console", "user_address": "999",
                                                         'HTTP_AUTHORIZATION': self.http_auth('test', 'nakulabye')})
        return fake_request

    def test_that_if_response_does_not_have_errors_accepted_is_true(self):
        mock_process_report = Mock()
        self.view.connection = None
        self.view.process_report = mock_process_report
        self.view.contact_exists = Mock(return_value=True)
        fake_request_factory = RequestFactory()
        fake_request = fake_request_factory.post('/', {"": ""})
        fake_request._raw_post_data = json.dumps({"report": "hello"})
        response = self.view.post(fake_request)
        self.assertEqual(mock_process_report.called, True)
        mock_process_report.assert_called_once_with("hello")

    def test_that_it_returns_a_400_response_if_the_json_is_in_the_wrong_format(self):
        fake_request_factory = RequestFactory()
        fake_request = fake_request_factory.post('/', {"": ""})
        self.view.connection = None
        self.view.contact_exists = Mock(return_value=True)
        fake_request._raw_post_data = "///sd"
        response = self.view.post(fake_request)
        self.assertEqual(400, response.status_code)

    def test_that_it_returns_a_400_if_the_json_has_no_key_response(self):
        fake_request_factory = RequestFactory()
        fake_request = fake_request_factory.post('/', {"": ""})
        self.view.connection = None
        self.view.contact_exists = Mock(return_value=True)
        fake_request._raw_post_data = "{}"
        response = self.view.post(fake_request)
        self.assertEqual(400, response.status_code)