from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from mock import Mock
from rapidsms.models import Connection, Backend
from rapidsms_httprouter.models import Message
from ureport.forms import ReplyTextForm


class FormTest(TestCase):

    def test_the_priority_of_a_reply_text_form(self):
        request_factory = RequestFactory()
        fake_request = request_factory.get('/')
        fake_user = Mock(return_value=User())
        fake_user.has_perm = Mock(return_value=True)
        fake_request.user = fake_user

        reply_text_form = ReplyTextForm({'text':'my message', 'results':'751234567'}, **{'request':fake_request})
        reply_text_form.cleaned_data = {'text':'my message'}
        backend, created = Backend.objects.get_or_create(name='test_backend')
        connection = Connection.objects.create(identity='751234567', backend=backend)
        message = Message.objects.create(text='received message', connection=connection)
        message_response, status = reply_text_form.perform(fake_request, Message.objects.filter(id=message.id))
        msg = Message.objects.get(text='my message')
        self.assertEqual(status,"success")
        self.assertIsNotNone(msg)
        self.assertIsNotNone(msg.batch)
        self.assertEqual(msg.batch.priority,10)
