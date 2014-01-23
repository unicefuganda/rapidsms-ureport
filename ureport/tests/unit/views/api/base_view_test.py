from unittest import TestCase
from django.test import RequestFactory
from rapidsms.models import Contact, Connection
from ureport.views.api.base import UReporterApiView


class BaseViewTest(TestCase):
    def test_is_called_with_backend_and_address(self):
        view = UReporterApiView()
        kwargs = {"backend": "console", "user_address": "999"}
        request_factory = RequestFactory()
        fake_request = request_factory.get('/')
        view.get(fake_request, None, **kwargs)
        self.assertEqual("console", view.backend_name)
        self.assertEqual("999", view.user_address)

    def test_that_contact_exists_when_connection_has_contact(self):
        view = UReporterApiView()
        connection = Connection(contact=Contact())
        self.assertEqual(True, view.contact_exists(connection))

    def test_that_contact_does_not_exist_if_there_is_no_connection(self):
        view = UReporterApiView()
        connection = None
        self.assertEqual(False, view.contact_exists(connection))