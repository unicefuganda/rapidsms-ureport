from unittest import TestCase
from django.contrib.auth.models import User
from poll.models import Poll, Response
from rapidsms_httprouter.models import Message
from rapidsms.models import Contact, Connection, Backend
from rapidsms.contrib.locations.models import Location
from ureport.spreadsheet_utils import get_poll_responses, get_formatted_responses_for_poll_per_district
from rapidsms.messages.incoming import IncomingMessage
from geoserver.models import PollData
import random

def _create_poll(contacts, user):
    poll = Poll.objects.create(
        name='test',
        type=Poll.TYPE_TEXT,
        question='test',
        default_response='yes',
        user = user
    )
    poll.contacts.add(contacts[0])
    poll.save()
    poll.add_yesno_categories()
    poll.start()
    return poll


def _get_incoming_message(connection, message):
    incoming_message = IncomingMessage(connection, message)
    incoming_message.db_message = Message.objects.create(direction='I', connection=connection, text=message)
    return incoming_message


class TestSpreadSheetUtils(TestCase):
    def test_excel_dump_report_for_poll(self):
        backend = Backend.objects.create(name='test_backend')
        connection = Connection.objects.create(identity='6262',backend=backend)
        contact = Contact.objects.create(name='test_contact')
        connection.contact = contact
        connection.save()
        user = User.objects.create(username='test',email='a@a.com')

        poll = _create_poll(contacts=[contact], user=user)
        poll.process_response(_get_incoming_message(connection, 'yes'))

        expected_response = [connection.identity, contact.name,
                             '', 'yes']

        responses = get_poll_responses(poll)

        self.assertEqual(1,len(responses))
        self.assertEqual(expected_response,responses[0])

    def test_per_district_report_for_yes_no_polls(self):
        for i in range(5):
            PollData.objects.using('geoserver').create(district='district%s' % i, poll_id = 1,
                deployment_id=1, yes = random.randint(0,10), no = random.randint(0,10),
                unknown = random.randint(0,10), uncategorized = random.randint(0,10))

        PollData.objects.using('geoserver').create(district='district1', poll_id = 2,
            deployment_id=1, yes = random.randint(0,10), no = random.randint(0,10),
            unknown = random.randint(0,10), uncategorized = random.randint(0,10))

        results = get_formatted_responses_for_poll_per_district(1)
        self.assertEqual(6, len(results))

    def tearDown(self):
        Backend.objects.all().delete()
        Connection.objects.all().delete()
        Contact.objects.all().delete()
        User.objects.all().delete()
        Poll.objects.all().delete()
        Message.objects.all().delete()
        Response.objects.all().delete()
        PollData.objects.using('geoserver').all().delete()
