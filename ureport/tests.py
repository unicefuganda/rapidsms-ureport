"""
Basic tests for RapidSMS-Ureport
"""

from django.test import TestCase
from models import Flag, MessageFlag
from rapidsms.models import Contact, Connection, Backend
from rapidsms.messages.incoming import IncomingMessage
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router

class ModelTest(TestCase): #pragma: no cover

    def setUp(self):
        """
        Create a dummy connection
        """

        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='11235811', backend=self.backend)
        #give the connection a contact
        self.connection.contact = Contact.objects.create(name='Anonymous User')
        self.connection.save()
        word_list=['zombies','inferi','waves','living dead','monsters']
        for word in word_list:
            flag=Flag.objects.create(name=word)

    def fakeIncoming(self, message, connection=None):
        if connection is None:
            connection = self.connection
        router = get_router()
        router.handle_incoming(connection.backend.name, connection.identity, message)

    def spoof_incoming_obj(self, message, connection=None):
        if connection is None:
            connection = Connection.objects.all()[0]
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=Connection.objects.all()[0], text=message)
        return incomingmessage


    def testflaggedmessage(self):
        connection = Connection.objects.all()[0]
        #create flagged messages

        incomingmessage = self.fakeIncoming('My village is being invaded by an army of zombies')
        self.assertEquals(MessageFlag.objects.count(), 1)


