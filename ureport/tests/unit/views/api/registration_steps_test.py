import base64
import json
import unittest
from poll.models import Poll
from script.models import Script, ScriptStep
from django.test import RequestFactory
from mock import Mock
from ureport.views.api.registration_steps import RegistrationStepsView


class RegistrationStepsTest(unittest.TestCase):

    def setUp(self):
        self.view = RegistrationStepsView()

    def test_that_the_ureport_autoreg2_is_called(self):
        registration_steps_view = RegistrationStepsView()

        Script.objects.filter = Mock(side_effect=self.script_side_effect)
        registration_script = registration_steps_view.get_registration_script()

        self.assertTrue(registration_script is not None)
        Script.objects.filter.assert_called_with(slug="ureport_autoreg2")

    def test_that_an_array_of_steps_is_returned(self):
        registration_steps_view = RegistrationStepsView()
        mocked_script = Mock()
        mocked_script.steps.all = Mock(return_value=["first step"])

        registration_steps = registration_steps_view.get_script_steps(mocked_script)

        self.assertEqual(registration_steps, ["first step"])

    def get_mocked_step_with_poll_question(self, question):
        mocked_poll = Poll()
        mocked_poll.question = question
        poll_step = ScriptStep()
        poll_step.poll = mocked_poll
        return poll_step

    def get_mocked_step_with_message(self, message):
        mocked_step_2 = ScriptStep()
        mocked_step_2.message = message
        return mocked_step_2

    def test_that_get_request_returns_all_the_steps(self):
        poll_step = self.get_mocked_step_with_poll_question("expected question")
        mocked_step_2 = self.get_mocked_step_with_message("expected message")
        Script.objects.filter = Mock(side_effect=self.script_side_effect)
        self.view.get_script_steps = Mock(return_value=[poll_step, mocked_step_2])
        response = self.get_http_response_from_view({}, self.view)
        data = json.loads(response.content)

        self.assertTrue("expected question" in data["steps"])
        self.assertTrue("expected message" in data["steps"])

    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        auth_string = base64.b64encode("who:why")
        fake_request = request_factory.get('/', **{"HTTP_AUTHORIZATION": ("Basic %s" % auth_string)})
        self.view.validate_credentials = Mock(return_value=True)
        return view.dispatch(fake_request, None, **kwargs)

    def script_side_effect(self, slug):
        if slug == "ureport_autoreg2":
            return [Script()]
        return None