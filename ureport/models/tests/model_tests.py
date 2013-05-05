# -*- coding: utf-8 -*-
"""
Basic tests for RapidSMS-Ureport
"""
from django.contrib.auth.models import User, Group

from django.test import TestCase
from contact.models import Flag, MessageFlag
from rapidsms.contrib.locations.models import Location,LocationType
from script.models import Script
from rapidsms.models import Contact, Connection, Backend
from unregister.models import Blacklist
from rapidsms.messages.incoming import IncomingMessage
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router
from django.core.management import call_command
from rapidsms_xforms.models import XForm
from poll.models import Poll
from script.utils.handling import find_closest_match
import re
from script.models import *
from django.core import management
from script.utils.incoming import incoming_progress
from script.utils.outgoing import check_progress
from django.core.management import call_command

class ModelTest(TestCase): #pragma: no cover
    fixtures = ['test_fix.json','0004_migration_initial_data.json','luo_translation.json','script2.json','script_luo.json','ussd.json']
    def setUp(self):
        """
        Create a dummy connection
        """




        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='2119271946678', backend=self.backend)
        self.connection1 = Connection.objects.create(identity='6262', backend=self.backend)
        self.connection2 = Connection.objects.create(identity='82764125', backend=self.backend)
        self.connection3 = Connection.objects.create(identity='256777773260', backend=self.backend)
        self.user,created=User.objects.get_or_create(username="admin")
        self.router=get_router()
        #create test contact
        self.connection.contact = Contact.objects.create(name='Anonymous User')
        self.connection.save()
        #create message flags
        word_list=['zombies','inferi','waves','living dead','monsters']
        for word in word_list:
            flag=Flag.objects.create(name=word)

        Flag.objects.create(name="jedi",words="luke,sky,walker,jedi",rule=2)
        #create test group
        self.gem_group=Group.objects.create(name="GEM")
        Location.objects.create(name="kampala",type=LocationType.objects.create(name="district",slug="district"))
        

    def fakeIncoming(self, message, connection):
        self.router.handle_incoming(connection.backend.name, connection.identity, message)

    def assertInteraction(self, connection, incoming_message, expected_response):
        incoming_obj = self.router.handle_incoming(connection.backend.name, connection.identity, incoming_message)
        self.assertEquals(Message.objects.filter(in_response_to=incoming_obj, text=expected_response).count(), 1)

    def spoof_incoming_obj(self, message, connection=None):
        if connection is None:
            connection = Connection.objects.all()[0]
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=Connection.objects.all()[0], text=message)
        return incomingmessage

    def elapseTime(self, progress, seconds):
        """
        This hack mimics the progression of time, from the perspective of a linear test case,
        by actually *subtracting* from the value that's currently stored (usually datetime.datetime.now())
        """
        progress.set_time(progress.time - datetime.timedelta(seconds=seconds))
        try:
            session = ScriptSession.objects.get(connection=progress.connection, end_time=None)
            session.start_time = session.start_time - datetime.timedelta(seconds=seconds)
            session.save()
        except ScriptSession.DoesNotExist:
            pass

    def fake_script_dialog(self, script_prog, connection, responses, emit_signal=True):
        script = script_prog.script
        ss = ScriptSession.objects.create(script=script, connection=connection, start_time=datetime.datetime.now())
        for poll_name, resp in responses:
            poll = script.steps.get(poll__name=poll_name).poll
            poll.process_response(self.spoof_incoming_obj(resp))
            resp = poll.responses.all().order_by('-date')[0]
            ScriptResponse.objects.create(session=ss, response=resp)
        ss.end_time = datetime.datetime.now()
        ss.save()
        if emit_signal:
            script_progress_was_completed.send(connection=connection, sender=script_prog)
        return ss

        
    def testflaggedmessage(self):
        #create flagged messages
        #reload the connection object
        connection=Connection.objects.all()[0]
        incomingmessage = self.fakeIncoming('My village is being invaded by an army of zombies',self.connection)
        self.assertEquals(MessageFlag.objects.count(), 1)
        incomingmessage = self.fakeIncoming('Luke skywalker is a Jedi',self.connection)
        self.assertEquals(MessageFlag.objects.count(), 2)

    def testyouthgrouppoll(self):
        groups=[u"GEM",u"gem",u"GEM group",u"it is GEM",u"yes GEM masaka group",u"yes GEM",u"Gem masaka",u"Girls Education Movement(GEM)",u"GEM-Uganda",u"YES GEM?§U",u"Yes Gem's chapter"]
        for gr in groups:
            for g in re.findall(r'\w+', gr):
                group = find_closest_match(g, Group.objects)
                if group:
                    self.assertEqual(self.gem_group,group)


    def test_quit(self):
        connection=Connection.objects.all()[0]
        incomingmessage = self.fakeIncoming('quit',self.connection)
        self.assertEquals(Blacklist.objects.count(), 1)
        self.assertEquals(Message.objects.order_by('-pk')[0].status, u'Q')

    # def test_autoreg(self):
    #
    #     #fake english join message
    #     inmsg1=self.fakeIncoming('join',self.connection1)
    #     #make sure a scrpt progress was created
    #     #get a response
    #     self.assertEquals(ScriptProgress.objects.count(), 1)
    #     script_prog1 = ScriptProgress.objects.all().order_by('pk')[0]
    #     #make sure script progress was assigned the right language
    #     self.assertEqual(script_prog1.language,"en")
    #     #make sure the connection was dumped into the right script
    #     self.assertEquals(script_prog1.script.slug, 'ureport_autoreg2')
    #
    #     res_count = Message.objects.filter(direction='O', connection=self.connection1).count()
    #     for script in Script.objects.all():
    #         check_progress(script)
    #
    #     response = Message.objects.filter(direction='O', connection=self.connection1)
    #     if response.exists() and not response.count() == res_count:
    #         response = response.latest('date').text
    #     else:
    #         response = None
    #     # we're ready for the first message to go out
    #
    #     self.assertEquals(response, script_prog1.script.steps.get(order=0).message)
    #
    #     self.fake_script_dialog(script_prog1, script_prog1.connection,
    #                             [\
    #         ('contactdistrict', 'kampala'), \
    #         ('contactname', 'lord voldmort'), \
    #         ('contactage', '19'), \
    #         ('contactgender', 'm'), \
    #         ('contactvillage', 'makindye'), \
    #         ('youthgroup', 'foo'), \
    #     ])
    #
    #     contact1 = Contact.objects.get(connection=script_prog1.connection)
    #     self.assertEquals(contact1.language,'en')
    #
    #     #fake luo join message
    #     self.fakeIncoming('Donyo',self.connection2)
    #
    #     #at this point 2 scripts shd have been created
    #     self.assertEquals(ScriptProgress.objects.count(), 2)
    #     script_prog2 = ScriptProgress.objects.order_by('pk')[1]
    #     #make sure the luo guy was dumped into the luo script
    #     self.assertEquals(script_prog2.script.slug, 'ureport_autoreg_luo2')
    #     res_count = Message.objects.filter(direction='O', connection=self.connection2).count()
    #     for script in Script.objects.all():
    #         check_progress(script)
    #
    #     response = Message.objects.filter(direction='O', connection=self.connection2)
    #     if response.exists() and not response.count() == res_count:
    #         response = response.latest('date').text
    #     else:
    #         response = None
    #     self.assertEquals(response, script_prog2.script.steps.get(order=0).message)
    #
    #     self.fake_script_dialog(script_prog2, script_prog2.connection,
    #                             [\
    #         ('contactdistrict', 'kampala'), \
    #         ('contactname', 'lord voldmort'), \
    #         ('contactage', '19'), \
    #         ('contactgender', 'm'), \
    #         ('contactvillage', 'makindye'), \
    #         ('youthgroup', 'foo'), \
    #     ])
    #
    #     contact2 = Contact.objects.get(connection=script_prog2.connection)
    #     self.assertEquals(contact2.language,'ach')

    def test_blacklist_poll(self):
        connection=Connection.objects.all()[0]
        incomingmessage = self.fakeIncoming('quit',self.connection)
        self.assertEquals(Blacklist.objects.count(), 1)
        # self.assertEqual(1,Poll.objects.get(name="blacklist").contacts.count())








