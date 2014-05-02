import base64
import json
import unittest
from django.db.models import Q
from poll.models import Poll, Translation
from script.models import Script, ScriptStep
from django.test import RequestFactory
from mock import Mock
import settings
from ureport.views.api.registration_steps import RegistrationStepsView


class RegistrationStepsTest(unittest.TestCase):

    def setUp(self):
        self.view = RegistrationStepsView()

    def test_multiple_registration_scripts_query_from_settings(self):
        registration_steps_view = RegistrationStepsView()
        settings.REGISTRATION_SCRIPTS = {"ureport_autoreg2": "en", "script_2": "es", "script_3": "de"}
        expected_query = Q(slug='ureport_autoreg2') | Q(slug='script_2') | Q(slug='script_3')

        query = registration_steps_view.get_registration_scripts_query()
        self.addTypeEqualityFunc(Q, self.are_queries_equal)
        self.assertEquals(expected_query, query)

    def test_multiple_registration_scripts_default_query(self):
        registration_steps_view = RegistrationStepsView()
        expected_query = Q(slug='ureport_autoreg2') | Q(slug='ureport_autoreg_luo2') | Q(slug='ureport_autoreg_kdj')

        query = registration_steps_view.get_registration_scripts_query()
        self.addTypeEqualityFunc(Q, self.are_queries_equal)
        self.assertEquals(expected_query, query)

    def test_that_the_registration_scripts_are_called(self):
        registration_steps_view = RegistrationStepsView()
        settings.REGISTRATION_SCRIPTS = {"ureport_autoreg2":"en", "ureport_autoreg_luo2":"ach"}
        Script.objects.filter = Mock(side_effect=self.script_side_effect)
        registration_scripts = registration_steps_view.get_registration_scripts()
        expected_script_names = [Script(slug='ureport_autoreg2'), Script(slug='ureport_autoreg_luo2')]

        self.assertListEqual(expected_script_names, registration_scripts)

    def test_that_an_array_of_steps_is_returned(self):
        registration_steps_view = RegistrationStepsView()
        mocked_script_1 = Mock()
        mocked_script_1.steps.all = Mock(return_value=["first step", "second step"])
        mocked_script_2 = Mock()
        mocked_script_2.steps.all = Mock(return_value=["third step"])

        registration_steps = registration_steps_view.get_script_steps([mocked_script_1, mocked_script_2])

        self.assertItemsEqual(registration_steps, ["first step", "second step", "third step"])

    def test_that_step_string_get_the_poll_translation(self):
        registration_steps_view = RegistrationStepsView()
        settings.REGISTRATION_SCRIPTS = {"ureport_autoreg2": "en", "ureport_autoreg_luo2": "ach"}

        poll_step = self.get_mocked_step_with_poll_question("expected question","ureport_autoreg2")
        poll_luo_step = self.get_mocked_step_with_poll_question("luo question", "ureport_autoreg_luo2")
        Translation.objects.get_or_create(field="luo question", language="ach", value="translated luo question")
        step_message = self.get_mocked_step_with_message("expected message")
        steps = [poll_step, step_message, poll_luo_step]

        steps_strings = registration_steps_view.get_step_strings(steps)

        self.assertItemsEqual([u'expected question', u'expected message', u'translated luo question'], steps_strings)

    def test_that_get_request_returns_all_unique_registration_steps(self):
        settings.REGISTRATION_SCRIPTS = {"registration_script": "en"}
        poll_step = self.get_mocked_step_with_poll_question("expected question", "registration_script")
        mocked_step_1 = self.get_mocked_step_with_message("expected message")
        mocked_step_2 = self.get_mocked_step_with_message("expected message")
        self.view.get_script_steps = Mock(return_value=[poll_step, mocked_step_1, mocked_step_2])
        response = self.get_http_response_from_view({}, self.view)
        data = json.loads(response.content)

        self.assertDictEqual(data, {u'steps': [u'expected question', u'expected message']})

    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        auth_string = base64.b64encode("who:why")
        fake_request = request_factory.get('/', **{"HTTP_AUTHORIZATION": ("Basic %s" % auth_string)})
        self.view.validate_credentials = Mock(return_value=True)
        return view.dispatch(fake_request, None, **kwargs)

    def script_side_effect(self, query):
        expected_query = Q(slug='ureport_autoreg2') | Q(slug='ureport_autoreg_luo2')
        if self.are_queries_equal(query, expected_query):
            return [Script(slug='ureport_autoreg2'), Script(slug='ureport_autoreg_luo2')]
        return None

    def are_queries_equal(self, first_query, other_query, msg=None):
        first_query.__dict__['children'].sort()
        other_query.__dict__['children'].sort()
        return type(first_query) is type(other_query) is Q and first_query.__dict__==other_query.__dict__

    def get_mocked_step_with_poll_question(self, question, script_slug='registration_script'):
        mocked_poll = Poll()
        mocked_poll.question = question
        poll_step = ScriptStep()
        poll_step.poll = mocked_poll
        poll_step.script = Script(slug=script_slug)
        return poll_step

    def get_mocked_step_with_message(self, message):
        mocked_step = ScriptStep()
        mocked_step.message = message
        return mocked_step