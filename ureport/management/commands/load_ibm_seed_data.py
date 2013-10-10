from django.contrib.auth.models import Group
from django.core.management import BaseCommand, execute_from_command_line
from django.core.exceptions import MultipleObjectsReturned
from rapidsms.models import Backend, Connection
from rapidsms_httprouter.models import Message
from message_classifier.models import IbmMsgCategory, IbmCategory

IBM_CLASSIFICATION_DUMMY = "IBM Dummy"


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.load_categories()
        categories = self.get_loaded_categories()
        self.create_seed_data(categories)

    def create_group(self):
        group, created = Group.objects.get_or_create(name=IBM_CLASSIFICATION_DUMMY)
        return group

    def create_backend(self, name):
        backend, created = Backend.objects.get_or_create(name=name)
        return backend

    def create_connection(self, backend, identity):
        connection, created = Connection.objects.get_or_create(backend=backend, identity=identity)
        return connection

    def create_message(self, connection, text, direction, status):
        return Message.objects.get_or_create(connection=connection, text=text, direction=direction, status=status)

    def load_categories(self):
        arguments = ["manage.py", "loaddata", "initial_categories"]
        execute_from_command_line(arguments)

    def get_loaded_categories(self):
        self.load_categories()
        return IbmCategory.objects.all()

    def create_ibm_message_category(self, message, category, score):
        message_category, created = IbmMsgCategory.objects.get_or_create(msg=message, category=category, score=score)
        return message_category

    def create_seed_data(self, categories):
        backend = self.create_backend(IBM_CLASSIFICATION_DUMMY)
        connection = self.create_connection(backend, "0772123456")

        for category in categories:
            try:
                message, created = self.create_message(connection, IBM_CLASSIFICATION_DUMMY, "I", "H")
                if created:
                    self.create_ibm_message_category(message, category, 0)
            except MultipleObjectsReturned:
                pass # No problem if there are already messages.

