import factory
from rapidsms.models import Connection
import datetime
from poll.models import Response
from rapidsms_ureport.ureport.tests.factories.backend_factory import BackendFactory
from rapidsms_ureport.ureport.tests.factories.contact_factory import ContactFactory
from rapidsms_ureport.ureport.tests.factories.message_factory import MessageFactory
from rapidsms_ureport.ureport.tests.factories.poll_factory import PollFactory


class ResponseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Response

    contact = factory.SubFactory(ContactFactory)
    message = factory.SubFactory(MessageFactory)
    poll = factory.SubFactory(PollFactory)
    date = datetime.datetime.now()
    has_errors = True
