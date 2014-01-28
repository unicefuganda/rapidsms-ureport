from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Backend, Connection
from script.models import ScriptSession, Script


class PollResponsesTestCase(TestCase):
    def test_that_url_for_poll_responses_returns_200(self):
        backend = Backend.objects.create(name="console")
        connection = Connection.objects.create(backend=backend, identity="999")
        script = Script.objects.create(slug="who")
        ScriptSession.objects.create(connection=connection, script=script)
        Poll.objects.create(id=1, user=User.objects.create(username="theone"), question="who")
        response = self.client.post("/api/v1/ureporters/console/999/poll/1/responses", {"{\"response\":\"Yes\"}": ""})
        self.assertEqual(200, response.status_code)

    def test_404_is_thrown_if_backend_does_not_exist(self):
        response = self.client.post("/api/v1/ureporters/console/999/poll/1/responses")
        self.assertEqual(404, response.status_code)



