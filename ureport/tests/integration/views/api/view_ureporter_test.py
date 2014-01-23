from django.test import TestCase
from rapidsms.models import Backend, Connection, Contact
from ureport.views.api.ViewUreporter import ViewUreporter


class ViewUreporterTest(TestCase):
    def test_that_retrieves_contact_formation(self):
        view = ViewUreporter()
        backend_name = "Console"
        user_address = "9922"
        view.backend_name = backend_name
        view.user_address = user_address
        backend,backend_created = Backend.objects.get_or_create(name=backend_name)
        connection,connection_created= Connection.objects.get_or_create(identity=user_address,backend=backend)
        contact = Contact.objects.create(name=user_address)
        connection.contact = contact
        connection.save()
        data = view.get_contact()
        self.assertEqual(True, data['registered'])
        self.assertEqual(contact.language, data['language'])

    def test_that_retrieves_contact_formation(self):
        view = ViewUreporter()
        backend_name = "Console"
        user_address = "9922"
        view.backend_name = backend_name
        view.user_address = user_address
        backend,backend_created = Backend.objects.get_or_create(name=backend_name)
        connection,connection_created= Connection.objects.get_or_create(identity=user_address,backend=backend)
        data = view.get_contact()
        self.assertEqual(False, data['registered'])
        self.assertEqual("", data['language'])