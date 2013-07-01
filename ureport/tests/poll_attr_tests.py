from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Connection, Contact
from uganda_common.utils import assign_backend
from ureport.models import PollAttribute, UPoll, PollAttributeValue

__author__ = 'kenneth'


class PollAttributeTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'test@pollattr.ken', password='testpassword')
        number, backend = assign_backend('+211927194678')
        connection = Connection.objects.create(identity=number, backend=backend)
        contact = Contact.objects.create(name='Test Contact')
        connection.contact = contact
        connection.save()
        poll = Poll.objects.create(name='Test Poll for poll attribute', question='Test question for test poll',
                                   user=user)
        poll.contacts.add(contact)
        poll.save()
        self.attr = PollAttribute.objects.create(key='viewable', key_type='bool', default=True)
        self.value = PollAttributeValue.objects.create(poll=poll, value=False)
        self.attr.values.add(self.value)

    def testCreate(self):
        self.assertEqual('true', self.attr.default)
        self.assertEqual(True, self.attr.get_default())


    def testAttrOnPoll(self):
        poll = UPoll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        self.assertEqual(False, poll.viewable)


    def testChangeAttr(self):
        poll = UPoll.objects.get(name='Test Poll for poll attribute', question='Test question for test poll')
        poll.viewable = True
        poll.save()
        value = PollAttributeValue.objects.get(poll=poll)
        self.assertEqual('true', value.value)
        self.assertEqual(True, value.get_value())
