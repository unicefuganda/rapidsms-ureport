import factory
from rapidsms.models import Connection
from rapidsms_ureport.ureport.tests.factories.backend_factory import BackendFactory
from rapidsms_ureport.ureport.tests.factories.contact_factory import ContactFactory


class ConnectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Connection

    backend = factory.SubFactory(BackendFactory)
    identity = "256763236262"
    contact = factory.SubFactory(ContactFactory)