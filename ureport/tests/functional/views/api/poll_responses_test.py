import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_liveserver.testcases import LiveServerTestCase
import requests
from poll.models import Poll
from rapidsms.models import Backend, Connection
from script.models import ScriptSession, Script


class PollResponsesTestCase(LiveServerTestCase):
    def server_url_for_path(self, url):
        return self.live_server_url + "%s" % url

    def test_that_url_for_poll_responses_returns_200(self):
        backend = Backend.objects.create(name="console")
        connection = Connection.objects.create(backend=backend, identity="999")
        script = Script.objects.create(slug="who")
        ScriptSession.objects.create(connection=connection, script=script)
        Poll.objects.create(id=900, user=User.objects.create(username="theone"), question="who")
        url = self.server_url_for_path(
            reverse("submit_poll_response_api", kwargs={"poll_id": 900, "backend": "console", "user_address": 999}))
        data = {"response": True}
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(200, response.status_code)

    def test_404_is_thrown_if_backend_does_not_exist(self):
        response = requests.post(self.server_url_for_path("/api/v1/ureporters/console/999/poll/1/responses"))
        self.assertEqual(404, response.status_code)




