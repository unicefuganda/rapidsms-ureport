import json
from django.core.urlresolvers import reverse
from django.test import TestCase
from rapidsms.models import Backend, Connection, Contact
from ureport.tests.functional.views.api.helpers import TestBasicAuthMixin


class SubmitReportTestCase(TestCase, TestBasicAuthMixin):
    def test_that_you_can_submit_the_report_if_you_are_registered(self):
        backend = Backend.objects.create(name="console")
        contact = Contact.objects.create(name="annont")
        connection = Connection.objects.create(backend=backend, identity="999", contact=contact)
        url = reverse("submit_report_api", kwargs={"backend": "console", "user_address": "999"})
        response = self.client.post(url, data=json.dumps({"report": "hello"}), content_type='application/json',
                                    **(self.get_auth_headers()))
        self.assertEqual(200, response.status_code)