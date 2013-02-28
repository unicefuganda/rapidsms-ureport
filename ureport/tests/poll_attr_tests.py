from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Connection, Contact
from uganda_common.utils import assign_backend
from ureport.models import PollAttribute, UPoll

__author__ = 'kenneth'


class PollAttributeTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'test@pollattr.ken', password='testpassword')
        number, backend = assign_backend('2567982888221')
        connection = Connection.objects.create(identity=number, backend=backend)
        contact = Contact.objects.create(name='Test Contact')
        connection.contact = contact
        connection.save()
        poll = Poll.objects.create(name='Test Poll for poll attribute', question='Test question for test poll',
                                   user=user)
        poll.contacts.add(contact)
        poll.save()

    def testCreate(self):
        poll = Poll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        attr = PollAttribute.objects.create_attr('viewable', True, poll, default=True)
        self.assertTrue(PollAttribute.objects.filter(key='viewable', poll=poll).exists())
        self.assertEqual(attr.key, 'viewable')
        self.assertEqual(attr.value, 'true')
        self.assertEqual(attr.key_type, 'bool')

    def test_get_default(self):
        poll = Poll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        attr = PollAttribute.objects.create_attr('viewable', True, poll, default=True)
        self.assertTrue(PollAttribute.objects.filter(key='viewable', poll=poll).exists())
        self.assertEqual(attr.get_default(), True)

    def test_set_default(self):
        poll = Poll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        attr = PollAttribute.objects.create_attr('viewable', True, poll, default=True)
        self.assertTrue(PollAttribute.objects.filter(key='viewable', poll=poll).exists())
        self.assertEqual(attr.get_default(), True)
        attr.set_default(False)
        self.assertEqual(attr.get_default(), False)

    def test_get_upoll_attr(self):
        poll = UPoll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        attr = PollAttribute.objects.create_attr('viewable', True, poll, default=True)
        self.assertTrue(PollAttribute.objects.filter(key='viewable', poll=poll).exists())
        self.assertEqual(poll.get_attr('viewable'), True)

    def test_set_upoll_attr(self):
        poll = UPoll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        attr = PollAttribute.objects.create_attr('viewable', True, poll, default=True)
        self.assertTrue(PollAttribute.objects.filter(key='viewable', poll=poll).exists())
        self.assertEqual(poll.get_attr('viewable'), True)
        poll.set_attr('viewable', False)
        self.assertEqual(poll.get_attr('viewable'), False)


    def test_set_upoll_default(self):
        poll = UPoll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        attr = PollAttribute.objects.create_attr('viewable', True, poll, default=True)
        self.assertTrue(PollAttribute.objects.filter(key='viewable', poll=poll).exists())
        UPoll.set_default_for_key('viewable', False)
        self.assertEqual(attr.get_default(),False)