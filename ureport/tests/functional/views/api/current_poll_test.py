
from django.test import TestCase
from rapidsms.models import Backend
from script.models import Script, ScriptStep


class CurrentPollTestCase(TestCase):
    def test_url_for_current_poll_returns_200(self):
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        first_step = ScriptStep.objects.create(script=script, order=1)
        backend,created = Backend.objects.get_or_create(name="console")
        response = self.client.get("/ureporters/console/999/polls/current")
        self.assertEqual(200, response.status_code)
