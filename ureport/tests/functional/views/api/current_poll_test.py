from django.test import TestCase
from rapidsms.models import Backend
from script.models import Script, ScriptStep
from ureport.tests.functional.views.api.helpers import TestBasicAuthMixin


class CurrentPollTestCase(TestCase, TestBasicAuthMixin):
    def test_url_for_current_poll_returns_200(self):
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        first_step = ScriptStep.objects.create(script=script, order=1)
        backend, created = Backend.objects.get_or_create(name="console")
        response = self.client.get("/api/v1/ureporters/console/999/polls/current", **(self.get_auth_headers()))
        self.assertEqual(200, response.status_code)

    def test_view_returns_404_if_backend_does_not_exist(self):
        response = self.client.get("/api/v1/ureporters/console/999/polls/current", **(self.get_auth_headers()))
        self.assertEqual(404, response.status_code)
