# -*- coding: utf-8 -*-
"""
Basic tests for RapidSMS-Ureport
"""
from httplib import HTTPException
import simplejson as json
import re

from django.contrib.auth.models import User, Group
from django.test import TestCase

from contact.models import Flag, MessageFlag
from poll.models import poll_started
from rapidsms.contrib.locations.models import Location, LocationType
from rapidsms.messages import IncomingMessage
from rapidsms.models import Contact, Connection, Backend
from script.models import ScriptSession, ScriptResponse
from script.signals import script_progress_was_completed
from unregister.models import Blacklist
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router
from script.utils.handling import find_closest_match
from script.models import *
from script.utils.outgoing import check_progress
from ureport.models import add_poll_to_blacklist
from mock import patch, Mock
from ureport.models.litseners import add_poll_recipients_to_blacklist


class UreportMessagesTestCase(TestCase):
    def fake_script_dialog(self, script_prog, connection, responses, emit_signal=True):
        script = script_prog.script
        ScriptSession.objects.filter(script=script, connection=connection).delete()
        script_session = ScriptSession.objects.create(script=script, connection=connection, start_time=datetime.datetime.now())

        for poll_name, resp in responses:
            poll = script.steps.get(poll__name=poll_name).poll
            poll.process_response(self.spoof_incoming_obj(resp, connection))
            resp = poll.responses.all().order_by('-date')[0]

            script_response = ScriptResponse.objects.create(session=script_session, response=resp)
            script_session.responses.add(script_response)

        script_session.end_time = datetime.datetime.now()
        script_session.save()

        if emit_signal:
            script_progress_was_completed.send(connection=connection, sender=script_prog)
        return script_session

    def fakeIncoming(self, message, connection):
        self.router = get_router()
        self.router.handle_incoming(connection.backend.name, connection.identity, message)

    def spoof_incoming_obj(self, message, connection=None):
        if connection is None:
            connection = Connection.objects.all()[0]
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=connection,
                                                            text=message)
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


class ModelTest(UreportMessagesTestCase): #pragma: no cover
    fixtures = ['test_fix.json', '0004_migration_initial_data.json', 'luo_translation.json', 'script2.json',
                'script_luo.json', 'ussd.json']

    def setUp(self):
        """
        Create a dummy connection
        """

        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='11235811', backend=self.backend)
        self.connection1 = Connection.objects.create(identity='4162549', backend=self.backend)
        self.connection2 = Connection.objects.create(identity='82764125', backend=self.backend)
        self.connection3 = Connection.objects.create(identity='256777773260', backend=self.backend)
        self.connection4 = Connection.objects.create(identity='25677771234', backend=self.backend)

        self.user, created = User.objects.get_or_create(username="admin")
        self.router = get_router()
        #create test contact
        self.connection.contact = Contact.objects.create(name='Anonymous User')
        self.connection.save()
        #create message flags
        word_list = ['zombies', 'inferi', 'waves', 'living dead', 'monsters']
        for word in word_list:
            flag = Flag.objects.create(name=word)

        Flag.objects.create(name="jedi", words="luke,sky,walker,jedi", rule=2)
        #create test group
        self.gem_group = Group.objects.create(name="GEM")
        Location.objects.create(name="kampala", type=LocationType.objects.create(name="district", slug="district"))

    def assertInteraction(self, connection, incoming_message, expected_response):
        incoming_obj = self.router.handle_incoming(connection.backend.name, connection.identity, incoming_message)
        self.assertEquals(Message.objects.filter(in_response_to=incoming_obj, text=expected_response).count(), 1)

    def testflaggedmessage(self):
        #create flagged messages
        #reload the connection object
        connection = Connection.objects.all()[0]
        incomingmessage = self.fakeIncoming('My village is being invaded by an army of zombies', self.connection)
        self.assertEquals(MessageFlag.objects.count(), 1)
        incomingmessage = self.fakeIncoming('Luke skywalker is a Jedi', self.connection)
        self.assertEquals(MessageFlag.objects.count(), 2)

    def testyouthgrouppoll(self):
        groups = [u"GEM", u"gem", u"GEM group", u"it is GEM", u"yes GEM masaka group", u"yes GEM", u"Gem masaka",
                  u"Girls Education Movement(GEM)", u"GEM-Uganda", u"YES GEM?§U", u"Yes Gem's chapter"]
        for gr in groups:
            for g in re.findall(r'\w+', gr):
                group = find_closest_match(g, Group.objects)
                if group:
                    self.assertEqual(self.gem_group, group)


    def test_quit(self):
        connection = Connection.objects.all()[0]
        incomingmessage = self.fakeIncoming('quit', self.connection)
        self.assertEquals(Blacklist.objects.count(), 1)
        self.assertEquals(Message.objects.order_by('-pk')[0].status, u'Q')

    def test_autoreg2_language_language_is_english(self):
        self.fakeIncoming('join', self.connection1)

        self.assertEquals(ScriptProgress.objects.count(), 1)

        registration_script_progress = ScriptProgress.objects.all().order_by('pk')[0]

        self.assertEquals((registration_script_progress).script.slug, 'ureport_autoreg2')
        self.assertEqual((registration_script_progress).language, "en")

    def fake_incoming_message_and_check_script_progress(self, incoming_message_text, connection=None):
        connection = self.connection1 if connection is None else connection
        self.fakeIncoming(incoming_message_text, connection)

        self.assertEquals(ScriptProgress.objects.count(), 1)

        registration_script_progress = ScriptProgress.objects.all().order_by('-pk')[0]

        check_progress(registration_script_progress.script)

        return registration_script_progress

    def test_response_the_user_receives_is_the_first_step_of_autoreg2(self):
        registration_script_progress = self.fake_incoming_message_and_check_script_progress('join')

        responses_from_connection = Message.objects.filter(direction='O', connection=self.connection1)

        response = responses_from_connection.latest('date').text if responses_from_connection.exists() else None

        script_step_message = (registration_script_progress).script.steps.get(order=0).message

        self.assertEquals(response, script_step_message)

    def test_when_user_sends_the_desired_opt_in_word_and_provides_all_the_neccessary_information_a_contact_should_be_created(
            self):
        registration_script_progress = self.fake_incoming_message_and_check_script_progress('join')

        self.fake_script_dialog(registration_script_progress, (
            registration_script_progress).connection,
                                [ \
                                    ('contactdistrict', 'kampala'), \
                                    ('contactage', '19'), \
                                    ('contactgender', 'm'), \
                                    ('contactvillage', 'makindye'), \
                                    ])

        self.assertEquals((Contact.objects.get(connection=(registration_script_progress).connection)).language, 'en')

    def change_village_name_poll_type_to_be_text(self):
        village_poll = Poll.objects.get(id=126)
        village_poll.type = 't'
        village_poll.save()

    def generate_contact(self, connection, poll_responses):
        registration_script_progress = self.fake_incoming_message_and_check_script_progress('join', connection)
        self.fake_script_dialog(registration_script_progress, connection, poll_responses)

    def test_contact_is_generated(self):
        self.change_village_name_poll_type_to_be_text()
        connection = self.connection4
        village_name = 'bukoto'
        poll_responses = [('contactdistrict', 'kampala'), ('contactage', '29'),
                          ('contactgender', 'female'), ('contactvillage', village_name), ]
        self.generate_contact(connection, poll_responses)

        kampala = Location.objects.get(name='kampala')
        contact_attributes = {'connection': connection, 'reporting_location': kampala,
                              'gender': 'F', 'village_name': village_name}

        contact = Contact.objects.filter(**contact_attributes)

        self.assertEquals(1, contact.count())

    def test_when_user_sends_a_village_with_more_than_100_characters_should_error(self):
        self.change_village_name_poll_type_to_be_text()
        connection = self.connection4
        village_name_with_more_than_100_characters = 'a'*101
        poll_responses = [('contactdistrict', 'kampala'), ('contactage', '29'),
                          ('contactgender', 'female'), ('contactvillage', village_name_with_more_than_100_characters), ]
        self.generate_contact(connection, poll_responses)

        kampala = Location.objects.get(name='kampala')
        contact_attributes = {'connection': connection, 'reporting_location': kampala,
                              'gender': 'F'}

        contact = Contact.objects.get(**contact_attributes)

        self.assertEquals('a'*100, contact.village_name)

    def test_autoreg_luo(self):
        #fake luo join message
        donyo = 'Donyo'
        self.fakeIncoming(donyo, self.connection2)

        #at this point 1 script shd have been created
        self.assertEquals(ScriptProgress.objects.count(), 1)
        script_prog2 = ScriptProgress.objects.order_by('pk')[0]
        #make sure the luo guy was dumped into the luo script
        self.assertEquals(script_prog2.script.slug, 'ureport_autoreg_luo2')
        res_count = Message.objects.filter(direction='O', connection=self.connection2).count()
        check_progress(script_prog2.script)

        response = Message.objects.filter(direction='O', connection=self.connection2)
        if response.exists() and not response.count() == res_count:
            response = response.latest('date').text
        else:
            response = None
        self.assertEquals(response, script_prog2.script.steps.get(order=0).message)

        self.fake_script_dialog(script_prog2, script_prog2.connection,
                                [ \
                                    ('contactdistrict', 'kampala'), \
                                    ('contactage', '19'), \
                                    ('contactgender', 'm'), \
                                    ('contactvillage', 'makindye'), \
                                    ])

        contact2 = Contact.objects.get(connection=script_prog2.connection)
        self.assertEquals(contact2.language, 'ach')

    def test_blacklist_poll(self):
        incomingmessage = self.fakeIncoming('quit', self.connection)
        self.assertEquals(Blacklist.objects.count(), 1)

    @patch('requests.post')
    def test_that_it_sends_poll_information_to_prioritizer_api(self, post_mock):
        poll = Poll(pk=123, question="My important question", default_response="Thanks")
        blacklist_poll_data_url = "http://www.my_api.com"
        settings.BLACKLIST_POLL_DATA_URL = blacklist_poll_data_url
        response_mock = Mock()
        response_mock.status_code = 200
        post_mock.return_value = response_mock

        add_poll_to_blacklist(poll)

        post_mock.assert_called_once_with(blacklist_poll_data_url, data={'poll_text': 'My important question', 'poll_id': '123', 'poll_response': 'Thanks'})

    @patch('requests.post')
    def test_that_no_sends_poll_information_to_prioritizer_api_when_url_does_not_exist(self, post_mock):
        poll = Poll(pk=123, question="My important question", default_response="Thanks")
        settings.BLACKLIST_POLL_DATA_URL = None
        add_poll_to_blacklist(poll)
        self.assertEquals(post_mock.call_count, 0)

    @patch('requests.post')
    def test_that_send_poll_information_to_prioritizer_api_throws_http_exception(self, post_mock):
        poll = Poll(pk=123, question="My important question", default_response="Thanks")
        settings.BLACKLIST_POLL_DATA_URL = "www.server.com"
        post_mock.return_value = HTTPException()
        self.assertRaises(Exception, add_poll_to_blacklist(poll))

    @patch('requests.post')
    def test_that_send_poll_contact_to_prioritizer_api_when_url_exists(self, post_mock):
        user = User.objects.create_user('test', 'test@test.com', password='test_password')
        backend, backend_created = Backend.objects.get_or_create(name='test_backend')
        connection, connection_created = Connection.objects.get_or_create(identity='25612345678', backend=backend)
        contact = Contact.objects.create(name='Test Contact')
        connection.contact = contact
        connection.save()
        poll = Poll.objects.create(id=999, name='Test Poll', question='question for test poll', user=user)
        poll.contacts.add(contact)
        poll.save()

        settings.BLACKLIST_POLL_RECIPIENTS_URL = "http://fake.com"
        response_mock = Mock()
        response_mock.status_code = 200
        post_mock.return_value = response_mock

        add_poll_recipients_to_blacklist(poll)
        data = json.dumps([u'25612345678'])
        params = {'poll_id': 999}
        post_mock.assert_called_once_with("http://fake.com", data=data, params=params)

    @patch('requests.post')
    def test_that_send_poll_contact_to_prioritizer_api_when_url_exists(self, post_mock):
        poll = Poll(pk=123, question="My important question", default_response="Thanks")
        settings.BLACKLIST_POLL_DATA_URL = None
        add_poll_recipients_to_blacklist(poll)
        self.assertEquals(post_mock.call_count, 0)

    @patch('requests.post')
    def test_that_send_poll_contact_to_prioritizer_api_when_url_exists(self, post_mock):
        poll = Poll(pk=123, question="My important question", default_response="Thanks")
        settings.BLACKLIST_POLL_DATA_URL = "http://fake.com"
        post_mock.return_value = HTTPException()
        self.assertRaises(Exception, add_poll_recipients_to_blacklist(poll))

    def test_add_poll_recipients_to_blacklist_part_of_poll_started_signal(self):
        registered_functions = [r[1] for r in poll_started.receivers]
        self.assertIn(add_poll_recipients_to_blacklist, registered_functions)

    def test_add_poll_to_blacklist_part_of_poll_started_signal(self):
        registered_functions = [r[1] for r in poll_started.receivers]
        self.assertIn(add_poll_to_blacklist, registered_functions)