# -*- coding: utf-8 -*-
"""
Basic tests for RapidSMS-Ureport
"""
from django.contrib.auth.models import User, Group

from django.test import TestCase
from models import Flag, MessageFlag, Script
from rapidsms.models import Contact, Connection, Backend
from rapidsms.messages.incoming import IncomingMessage
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router
from django.core.management import call_command
from rapidsms_xforms.models import XForm
from poll.models import Poll
from script.utils.handling import find_closest_match
import re

class ModelTest(TestCase): #pragma: no cover

    def setUp(self):
        """
        Create a dummy connection
        """

        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='11235811', backend=self.backend)
        self.user,created=User.objects.get_or_create(username="admin")
        self.router=get_router()
        #create test contact
        self.connection.contact = Contact.objects.create(name='Anonymous User')
        self.connection.save()
        #create message flags
        word_list=['zombies','inferi','waves','living dead','monsters']
        for word in word_list:
            flag=Flag.objects.create(name=word)
        #create test group
        self.gem_group=Group.objects.create(name="GEM")


    def fakeIncoming(self, message, connection):
        self.router.handle_incoming(connection.backend.name, connection.identity, message)

    def assertInteraction(self, connection, incoming_message, expected_response):
        incoming_obj = self.router.handle_incoming(connection.backend.name, connection.identity, incoming_message)
        self.assertEquals(Message.objects.filter(in_response_to=incoming_obj, text=expected_response).count(), 1)

    def testflaggedmessage(self):
        #create flagged messages
        #reload the connection object
        connection=Connection.objects.all()[0]
        incomingmessage = self.fakeIncoming('My village is being invaded by an army of zombies',self.connection)
        self.assertEquals(MessageFlag.objects.count(), 1)

    def testyouthgrouppoll(self):
        groups=[u"GEM",u"gem",u"GEM group",u"it is GEM",u"yes GEM masaka group",u"yes GEM",u"Gem masaka",u"Girls Education Movement(GEM)",u"GEM-Uganda",u"YES GEM?§U",u"Yes Gem's chapter"]
        for gr in groups:
            for g in re.findall(r'\w+', gr):
                group = find_closest_match(g, Group.objects)
                if group:
                    break
            self.assertEqual(self.gem_group,group)


    def testPost_syncdb_handlers(self):
         #call syncdb
         call_command("syncdb")
         self.assertEquals(Script.objects.count(),1)
         self.assertEquals(Poll.objects.count(), 6)




