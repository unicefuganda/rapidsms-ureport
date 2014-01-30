import json
from unittest import TestCase
from django.http import Http404
from django.test import RequestFactory
from mock import Mock
from rapidsms.models import Backend, Connection, Contact
from ureport.views.api.poll_topics import PollTopicsApiView


class PollTopicsTestCase(TestCase):
    def setUp(self):
        self.view = PollTopicsApiView()
        self.request_factory = RequestFactory()

    def test_that_post_returns_405_status_code(self):
        fake_request = self.request_factory.post("/")
        response = self.view.post(fake_request)
        self.assertEqual(405, response.status_code)

    def test_that_if_the_backend_does_not_exist_you_get_a_404(self):
        fake_request = self.request_factory.get("/", **{"backend": "console", "user_address": "999"})
        with self.assertRaises(Http404):
            self.view.dispatch(fake_request)

    def setup_get_request(self, backend, connection):
        self.view.get_backend = Mock(return_value=backend)
        self.view.get_connection = Mock(return_value=connection)
        fake_request = self.request_factory.get("/", **{"backend": "console", "user_address": "999"})
        return fake_request

    def test_that_if_the_user_address_does_not_exist_you_get_a_404(self):
        backend = Backend(id=89)
        connection = Connection(identity=999, backend=backend)
        fake_request = self.setup_get_request(backend, connection)
        with self.assertRaises(Http404):
            self.view.dispatch(fake_request)

    def test_that_if_there_are_no_polls_for_the_user_it_returns_success_and_an_empty_list(self):
        backend = Backend(id=89)
        connection = Connection(identity=999, backend=backend, contact=Contact())
        fake_request = self.setup_get_request(backend, connection)
        self.view.get_polls_for_contact = Mock(return_value=[])
        response = self.view.dispatch(fake_request)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual([], data['poll_topics'])
