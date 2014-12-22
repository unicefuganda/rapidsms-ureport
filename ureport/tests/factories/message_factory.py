import factory
import datetime

from rapidsms_httprouter_src.rapidsms_httprouter.models import Message
from rapidsms_ureport.ureport.tests.factories.connection_factory import ConnectionFactory


class MessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Message

    connection = factory.SubFactory(ConnectionFactory)
    text = "We shall override"
    direction = "O"
    status = "S"
    date = datetime.datetime.now()