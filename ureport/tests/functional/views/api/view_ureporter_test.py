from django.test import TestCase
from rapidsms.models import Backend, Connection, Contact


class ViewUreporterTestCase(TestCase):
    def test_view_ureporter_api_url_for_new_ureport_user(self):
        backend, backend_created = Backend.objects.get_or_create(name="console")
        response = self.client.get("/api/v1/ureporters/console/999")
        self.assertEqual(404, response.status_code)

    def test_view_ureporter_api_url_for_exisiting_ureport_user(self):
        backend_name = "console"
        user_address = "999"
        backend, backend_created = Backend.objects.get_or_create(name=backend_name)
        connection, connection_created = Connection.objects.get_or_create(identity=user_address, backend=backend)
        contact = Contact.objects.create(name=user_address)
        connection.contact = contact
        connection.save()
        response = self.client.get("/api/v1/ureporters/console/999")
        self.assertEqual(200, response.status_code)
