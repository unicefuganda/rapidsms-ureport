from unittest import TestCase
from message_classifier.models import IbmCategory, IbmMsgCategory
from rapidsms.models import Backend, Connection
from rapidsms_httprouter.models import Message
from rapidsms_ureport.ureport.management.commands.load_ibm_seed_data import Command


class LoadIbmSeedDataTest(TestCase):

    ANY_CONNECTION_IDENTITY = "0772334455"
    ANY_TEXT = "IBM Classifier Dummy"
    INCOMING = "I"

    categories_loaded = False
    categories_with_messages_inserted = []

    def setUp(self):
        print "setting up"
        self.load_ibm_seed_data = Command()

    def tearDown(self):
        Backend.objects.all().delete()
        Connection.objects.all().delete()
        IbmCategory.objects.all().delete()
        IbmMsgCategory.objects.all().delete()

    def test_should_insert_a_message_into_http_router_messages_table(self):
        self.assertEquals(1, 1)

    def test_should_insert_backend(self):
        self.create_backend()

        backend = Backend.objects.get(name=self.ANY_TEXT)

        self.assertIsNotNone(backend)

    def test_should_insert_connection_given_a_backend(self):
        connection = self.create_connection()

        connection = Connection.objects.get(pk=connection.id)

        self.assertIsNotNone(connection)

    def test_should_insert_message_given_a_connection(self):
        connection = self.create_connection()
        self.create_message(connection)

        message = Message.objects.get(connection=connection, direction=self.INCOMING)

        self.assertIsNotNone(message)

    def test_should_insert_ibm_message_category(self):
        connection = self.create_connection()
        message, created = self.create_message(connection)

        self.load_ibm_seed_data.load_categories()
        category = IbmCategory.objects.all()[0]

        self.load_ibm_seed_data.create_ibm_message_category(message=message, category=category, score=0.0123456789)
        expected_category = IbmMsgCategory.objects.get(msg=message)

        self.assertIsNotNone(expected_category)

    def load_classifier_categories(self):
        self.categories_loaded = True

    def test_should_load_categories_on_handle(self):
        self.load_ibm_seed_data.load_categories = self.load_classifier_categories

        self.load_ibm_seed_data.handle()

        self.assertTrue(self.categories_loaded)

    def test_should_load_twelve_categories_if_no_categories_exist(self):
        num_categories_before = len(IbmCategory.objects.all())

        self.load_ibm_seed_data.load_categories()
        num_categories_after = len(IbmCategory.objects.all())

        self.assertEquals(num_categories_before, 0)
        self.assertEquals(num_categories_after, 12)

    def test_should_only_load_categories_once(self):
        self.load_ibm_seed_data.load_categories()
        self.load_ibm_seed_data.load_categories()
        self.assertEquals(len(IbmCategory.objects.all()), 12)

    def test_should_insert_a_classifier_message_for_each_category(self):
        categories = self.create_dummy_categories()

        self.load_ibm_seed_data.create_ibm_message_category = self.create_ibm_message_category_mock
        self.load_ibm_seed_data.create_backend = lambda name: Backend(name=name)
        self.load_ibm_seed_data.create_connection = lambda backend, identity: Connection(backend=backend,
                                                                                         identity=identity)
        self.load_ibm_seed_data.create_message = lambda connection, text, direction, status: (Message(
            connection=connection, text=text, direction=direction, status=status), True)

        self.load_ibm_seed_data.create_seed_data(categories)

        self.assertEquals(self.categories_with_messages_inserted, categories)

    create_seed_data_called = False

    def test_should_call_create_seed_data_on_handle(self):
        self.load_ibm_seed_data.create_seed_data = self.create_seed_data_mock

        self.load_ibm_seed_data.handle()

        self.assertTrue(self.create_seed_data_called)

    def create_seed_data_mock(self, categories):
        self.create_seed_data_called = True

    def create_backend(self):
        return self.load_ibm_seed_data.create_backend(name=self.ANY_TEXT)

    def create_connection(self):
        backend = self.create_backend()
        connection = self.load_ibm_seed_data.create_connection(backend=backend, identity=self.ANY_CONNECTION_IDENTITY)

        return connection

    def create_message(self, connection):
        return self.load_ibm_seed_data.create_message(connection=connection, text=self.ANY_TEXT,
                                                      direction=self.INCOMING, status="H")

    def create_dummy_categories(self):
        dummy_categories = []
        for i in range(0, 12):
            dummy_categories.append(IbmCategory(pk=i, name="Category %d" % (i + 1)))
        return dummy_categories

    def create_ibm_message_category_mock(self, message, category, score):
        self.categories_with_messages_inserted.append(category)
