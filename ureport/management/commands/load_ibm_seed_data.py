from django.contrib.auth.models import Group
from django.core.management import BaseCommand, execute_from_command_line
from rapidsms.models import Contact, Backend, Connection
from rapidsms_httprouter.models import Message
from message_classifier.models import IbmMsgCategory, IbmCategory

IBM_CLASSIFICATION_DUMMY = "IBM Classification Dummy"


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.load_categories()

    def create_contact(self):
        Contact.objects.create(name=IBM_CLASSIFICATION_DUMMY)

    def create_group(self):
        group = Group.objects.create(name=IBM_CLASSIFICATION_DUMMY)
        return group

    def create_backend(self, name):
        return Backend.objects.create(name=name)

    def create_connection(self, backend, identity):
        return Connection.objects.create(backend=backend, identity=identity)

    def create_message(self, connection, text, direction, status):
        return Message.objects.create(connection=connection, text=text, direction=direction, status=status)

    def load_categories(self):
        arguments = ["manage.py", "loaddata", "initial_categories"]
        execute_from_command_line(arguments)

    def get_loaded_categories(self):
        self.load_categories()
        return IbmCategory.objects.all()

    def create_ibm_message_category(self, message, category, score):
        return IbmMsgCategory.objects.create(msg=message, category=category, score=score)

    def create_seed_data(self, categories):
        for category in categories:

            backend = self.create_backend(IBM_CLASSIFICATION_DUMMY)
            connection = self.create_connection(backend, "0772123456")
            message = self.create_message(connection, IBM_CLASSIFICATION_DUMMY, "I", "H")

            self.create_ibm_message_category(message, category, 0)