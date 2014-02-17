import base64
import unittest
import datetime
from django.http import Http404
import django.utils.simplejson as json
from django.test import RequestFactory
from mock import Mock, MagicMock
from poll.models import Poll
from rapidsms.models import Backend, Connection, Contact
from script.models import Script, ScriptProgress, ScriptStep
from ureport.views.api.currentpoll import ViewCurrentPoll


class CurrentPollTest(unittest.TestCase):
    def setUp(self):
        self.view = ViewCurrentPoll()

    def build_connection(self, contact=Contact()):
        return Connection(identity=77777, backend=Backend(name='my backend'), contact=contact)

    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        auth_string = base64.b64encode("who:why")
        fake_request = request_factory.get('/', **{"HTTP_AUTHORIZATION": ("Basic %s" % auth_string)})
        self.view.validate_credentials = Mock(return_value=True)
        return view.dispatch(fake_request, None, **kwargs)

    def setup_fake_connection(self):
        fake_connection = Mock()
        fake_connection.return_value = self.build_connection()
        self.view.get_connection = fake_connection

    def setup_fake_poll(self, fake_poll_return_value):
        fake_poll = Mock()
        fake_poll.return_value = fake_poll_return_value
        self.view.get_current_poll_for = fake_poll
        return fake_poll

    def test_404_is_raised_if_backend_does_not_exist(self):
        with self.assertRaises(Http404):
            response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)

    def test_that_in_case_of_post_it_raise_405(self):
        http_response = self.view.post(None)
        self.assertEqual(405, http_response.status_code)

    def test_that_poll_null_for_a_registered_user_with_no_poll(self):
        self.setup_fake_connection()
        self.setup_fake_poll(None)
        self.view.get_backend = Mock(return_value=Backend(name="my_backend"))
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual(None, data['poll'])

    def test_that_poll_data_for_a_registered_user_that_has_a_poll(self):
        self.setup_fake_connection()
        poll_data = {"id": 1, "name": "Test Poll", "question": "Is working?"}
        fake_poll = self.setup_fake_poll(poll_data)
        self.view.get_current_poll_for = fake_poll
        self.view.get_backend = Mock(return_value=Backend(name="my_backend"))
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual(poll_data, data['poll'])

    def test_that_for_an_unregistered_user_script_progress_object_is_created_if_it_does_not_exist(self):
        fake_connection = Mock()
        fake_connection.return_value = self.build_connection(None)
        self.view.get_connection = fake_connection
        self.view.get_current_step = Mock(return_value=None)
        self.view.get_script_progress = Mock(return_value=ScriptProgress(script=Script(slug="ureport_autoreg2")))
        self.view.get_backend = Mock(return_value=Backend(name="my_backend"))
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['success'])
        self.assertEqual("ureport_autoreg2", self.view.script_progress.script.slug)

    def test_that_retrieves_poll_data_from_step_of_script_progress(self):
        fake_connection = Mock()
        fake_connection.return_value = self.build_connection(None)
        self.view.get_connection = fake_connection
        self.view.get_script_progress = Mock(return_value=ScriptProgress(script=Script(slug="ureport_autoreg2")))
        fake_get_next_step = Mock(return_value=ScriptStep(poll=Poll(name="test poll", question="Is it working?")))
        self.view.get_current_step = fake_get_next_step
        self.view.get_backend = Mock(return_value=Backend(name="my_backend"))
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        data = json.loads(response.content)
        self.assertEqual(True, data['poll']['is_registration'])

    def test_that_data_from_poll_should_have_all_the_neccessary_fields(self):
        question = "is this really a poll ? or a pool ? or a loop?"
        name = "this is a poll"
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        default_response = "thanks"
        poll = Poll(name=name, question=question, id=12, type="t", start_date=an_hour_ago,
                    default_response=default_response, response_type="a")
        expected_poll_data = {"id": "12", "question": question, "name": name, "language": None, "question_voice": None,
                              "start_date": an_hour_ago.strftime(self.view.get_datetime_format()), "end_date": None,
                              "is_registration": False, "type": "t",
                              "default_response": default_response, "default_response_voice": None,
                              "response_type": "allow_all"}
        self.assertDictEqual(expected_poll_data, self.view.get_data_from_poll(poll))

    def test_that_if_the_step_is_a_message_the_poll_type_is_none(self):
        message = "hello hallo who aaa"
        fake_get_next_step = Mock(return_value=ScriptStep(message=message))
        self.view.get_current_step = fake_get_next_step
        expected_data = {"name": "Message", "question": message, "type": "none", "id": None}
        actual_data = self.view.get_data_from_message(message)
        self.assertDictEqual(expected_data, actual_data)

    def test_that_if_the_step_is_a_message_the_poll_id_is_none(self):
        message = "hello hallo who aaa"
        fake_get_next_step = Mock(return_value=ScriptStep(message=message))
        self.view.get_current_step = fake_get_next_step
        expected_data = {"name": "Message", "question": message, "type": "none", "id": None}
        actual_data = self.view.get_data_from_message(message)
        self.assertDictEqual(expected_data, actual_data)

    def test_that_script_progress_moves_on_when_current_step_is_message(self):
        self.setup_fake_connection()
        mock_progress = MagicMock()
        mock_progress.moveon = MagicMock()
        self.view.get_script_progress = Mock(return_value=mock_progress)
        self.view.contact_exists = Mock(return_value=False)
        self.view.get_current_step = Mock(return_value=ScriptStep(message="Welcome"))
        self.view.get_backend = Mock(return_value=Backend(name="my_backend"))
        response = self.get_http_response_from_view({"backend": "my_backend", "user_address": "77777"}, self.view)
        self.assertEqual(True, mock_progress.moveon.called)
