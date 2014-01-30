from django.test import TestCase
from rapidsms.models import Backend, Connection
from ureport.views.api.base import UReporterApiView


class BaseViewTest(TestCase):

    def test_get_connection_returns_connection_for_user_address(self):
        view = UReporterApiView()
        backend_name = "back"
        identity = "999"
        view.backend_name = backend_name
        view.user_address = identity
        view.backend, created = Backend.objects.get_or_create(name=backend_name)
        connection, connection_created = Connection.objects.get_or_create(identity=identity, backend=view.backend)
        self.assertEqual(connection.id, view.get_connection().id)
