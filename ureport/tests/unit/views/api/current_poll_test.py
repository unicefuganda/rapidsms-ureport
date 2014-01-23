import unittest
import django.utils.simplejson as json
from django.test import RequestFactory
from mock import Mock
from rapidsms.models import Backend, Connection, Contact
from script.models import Script, ScriptProgress
from ureport.views.api.currentpoll import ViewCurrentPoll


class CurrentPollTest(unittest.TestCase):
    def setUp(self):
        self.view = ViewCurrentPoll()

    def build_connection(self, contact=Contact()):
        return Connection(identity=77777, backend=Backend(name='my backend'), contact=contact)

    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        fake_request = request_factory.get('/')
        return view.get(fake_request, None, **kwargs)

    def setup_fake_connection(self):
        fake_connection = Mock()
        fake_connection.return_value = self.build_connection()
        self.view.get_connection = fake_connection

    def setup_fake_poll(self, none):
        fake_poll = Mock()
        fake_poll.return_value = none
        self.view.get_current_poll_for = fake_poll
        return fake_poll

    def test_that_poll_null_for_a_registered_user_with_no_poll(self):
        self.setup_fake_connection()
        self.setup_fake_poll(None)
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual(None, data['poll'])

    def test_that_poll_data_for_a_registered_user_that_has_a_poll(self):
        self.setup_fake_connection()
        poll_data = {"id": 1, "name": "Test Poll", "question": "Is working?"}
        fake_poll = self.setup_fake_poll(poll_data)
        self.view.get_current_poll_for = fake_poll
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual(poll_data, data['poll'])

    def test_that_for_an_unregistered_user_script_progress_object_is_created_if_it_does_not_exist(self):
        fake_connection = Mock()
        fake_connection.return_value = self.build_connection(None)
        self.view.get_connection = fake_connection
        self.view.get_script_progress = Mock(return_value=ScriptProgress(script=Script(slug="ureport_autoreg2")))
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual("ureport_autoreg2", self.view.script_progress.script.slug)

    # def test_that_if_the_script_progress_has_no_step_start_it(self):
    #     fake_connection = Mock()
    #     fake_connection.return_value = self.build_connection(None)
    #     self.view.get_connection = fake_connection
    #     self.view.get_script_progress = Mock(return_value=ScriptProgress(script=Script(slug="ureport_autoreg2")))
    #     response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
    #     data = json.loads(response.content)
    #     self.assertEqual(None, self.view.get_next_step())

