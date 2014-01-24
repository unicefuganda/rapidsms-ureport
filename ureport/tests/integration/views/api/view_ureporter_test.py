from django.test import TestCase
from rapidsms.models import Backend, Connection, Contact
from ureport.views.api.view_ureporter import ViewUReporter


class ViewUreporterTest(TestCase):
    def test_that_retrieves_contact_information_for_a_registered_user(self):
        view = ViewUReporter()
        backend_name = "Console"
        user_address = "9922"
        view.backend_name = backend_name
        view.user_address = user_address
        backend,backend_created = Backend.objects.get_or_create(name=backend_name)
        view.connection,connection_created= Connection.objects.get_or_create(identity=user_address,backend=backend)
        contact = Contact.objects.create(name=user_address)
        view.connection.contact = contact
        view.connection.save()
        data = view.get_contact()
        self.assertEqual(True, data['registered'])
        self.assertEqual(contact.language, data['language'])

    def test_that_retrieves_contact_information_for_a_non_registered_user(self):
        view = ViewUReporter()
        backend_name = "Console"
        user_address = "9922"
        view.backend_name = backend_name
        view.user_address = user_address
        backend,backend_created = Backend.objects.get_or_create(name=backend_name)
        view.connection,connection_created= Connection.objects.get_or_create(identity=user_address,backend=backend)
        data = view.get_contact()
        self.assertEqual(False, data['registered'])
        self.assertEqual("", data['language'])