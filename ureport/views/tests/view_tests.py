import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from poll.models import Poll
from django.contrib.auth.models import User

from rapidsms.models import Contact, Connection, Backend
from poll.models import Poll, Response, Category, Rule,Translation
from rapidsms_httprouter.router import get_router
from rapidsms_httprouter.models import Message
import datetime
from contact.models import Flag, MessageFlag

class TestViews(TestCase):
    fixtures = ['test_fix.json','Initial_data.json','luo_translation.json','script2.json','script_luo.json','ussd.json']
    def setUp(self):
        self.user,created = User.objects.get_or_create(username='admin')

        self.backend = Backend.objects.create(name='test')
        self.user2=User.objects.create_user('foo', 'foo@bar.net', 'barbar')

        self.contact1 = Contact.objects.create(name='John Jonny')
        self.connection1 = Connection.objects.create(backend=self.backend, identity='8675309', contact=self.contact1)

        self.contact2 = Contact.objects.create(name='gowl')
        self.connection2 = Connection.objects.create(backend=self.backend, identity='5555555', contact=self.contact2)
        self.test_msg=Message.objects.create(text="hello",direction="I",connection=self.connection1)
        self.poll = Poll.create_with_bulk(
            'test poll1',
            Poll.TYPE_TEXT,
            'test?',
            'test!',
            Contact.objects.filter(pk__in=[self.contact1.pk]),
            self.user)
        self.poll.start_date=datetime.datetime.now()
        self.cat1=self.poll.categories.create(name="cat1")
        self.cat2=self.poll.categories.create(name="cat2")
        self.cat3=self.poll.categories.create(name="cat3")
        self.resp = Response.objects.create(poll=self.poll, message=self.test_msg, contact=self.contact1, date=self.test_msg.date)
        self.flag=Flag.objects.create(name="jedi",words="luke,sky,walker,jedi",rule=2)


    def test_poll_dashboard(self):
        response = self.client.get(reverse('poll_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('poll_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        
        response = self.client.get(reverse('reporter-profile',kwargs={'pk':self.contact1.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('reporter-profile',kwargs={'pk':self.contact1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_polls(self):
        
        response = self.client.get(reverse('ureport-polls'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('ureport-polls'))
        self.assertEqual(response.status_code, 200)

    def test_scriptpolls(self):
        
        response = self.client.get(reverse('script-polls'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('script-polls'))
        self.assertEqual(response.status_code, 200)
    def test_massmessages(self):
        
        response = self.client.get(reverse('massmessages'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('massmessages'))
        self.assertEqual(response.status_code, 200)
    def test_messagelog(self):
        
        response = self.client.get(reverse('messagelog'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('messagelog'))
        self.assertEqual(response.status_code, 200)
    def test_quitmessages(self):
        
        response = self.client.get(reverse('quitmessages'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('quitmessages'))
        self.assertEqual(response.status_code, 200)
    def test_flaggedmessages(self):
        
        response = self.client.get(reverse('flaggedmessages'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('flaggedmessages'))
        self.assertEqual(response.status_code, 200)

    def test_flaggedwith(self):

        response = self.client.get(reverse('flagged_with',kwargs={'pk':self.flag.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('flagged_with',kwargs={'pk':self.flag.pk}))
        self.assertEqual(response.status_code, 200)
    def test_newflag(self):
        
        response = self.client.get(reverse('flags_new'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('flags_new'))
        self.assertEqual(response.status_code, 200)

    def test_poll_responses(self):
        
        response = self.client.get(reverse('responses',kwargs={'poll_id':self.poll.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('responses',kwargs={'poll_id':self.poll.pk}))
        self.assertEqual(response.status_code, 200)

    def test_bestviz(self):
        
        response = self.client.get(reverse('best-viz',kwargs={'poll_id':self.poll.pk}))
        self.assertEqual(response.status_code, 200)


    def test_signup(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_messaghistory(self):
        response = self.client.get(reverse('profile',kwargs={'connection_pk':self.connection1.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('profile',kwargs={'connection_pk':self.connection1.pk}))
        self.assertEqual(response.status_code, 200)
    def test_mpdashboard(self):
        response = self.client.get(reverse('mp_dashboard'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('mp_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_ussdmanager(self):
        response = self.client.get(reverse('ussd_manager'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('ussd_manager'))
        self.assertEqual(response.status_code, 200)


    def test_viewpoll(self):
        response = self.client.get(reverse('view_poll',kwargs={'pk':self.poll.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('view_poll',kwargs={'pk':self.poll.pk}))
        self.assertEqual(response.status_code, 200)

    def test_sendmessage(self):
        response = self.client.get(reverse('send_message'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('send_message'))
        self.assertEqual(response.status_code, 200)

    def test_editcategory(self):
        response = self.client.get(reverse('edit_category',kwargs={'pk':self.cat1.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('edit_category',kwargs={'pk':self.cat1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_grouprules(self):
        response = self.client.get(reverse('view_rules',kwargs={'pk':self.cat1.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('view_rules',kwargs={'pk':self.cat1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_alerts(self):
        response = self.client.get(reverse('alerts'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="foo",password="barbar")
        response = self.client.get(reverse('alerts'))
        self.assertEqual(response.status_code, 200)

    


