import time
from rapidsms.models import Contact,Connection, Backend
from splinter import Browser
from rapidsms.models import Contact
from rapidsms.models import Connection
from datetime import datetime

from ureport.tests.functional.splinter_wrapper import SplinterTestCase

BROWSER = Browser('firefox')

from ureport.tests.functional.test_utils import create_group, create_user, create_connection, create_poll,\
    add_contacts_to_poll

class PollStatusTest(SplinterTestCase):
    def setUp(self):
        self.browser = BROWSER

        group = create_group(group_name='poll_status_group')

        user1 = create_user(username="foo", email='foo@bar.com', group=group)
        user2 = create_user(username='fred', email='shaggy@scooby.com', group=group)

        contact1 = Contact.objects.create(pk=999, name='poll_status_contact_1', user=user1, gender='M', birthdate=datetime.now(), language="en")
        contact2 = Contact.objects.create(pk=1000, name='poll_status_contact_2', user=user2, gender='M', birthdate=datetime.now(), language="en")
        contacts = [contact1, contact2]

        backend = Backend.objects.create(name='PS_BACKEND')
        create_connection(identity='0794335546', contact=contact1, backend=backend)
        create_connection(identity='0794335529', contact=contact2, backend=backend)

        self.poll = create_poll(user2)
        add_contacts_to_poll(self.poll, contacts)

        self.poll.add_yesno_categories()

        self.create_and_sign_in_admin("argha", "a")

        self.open("/poll_status/%s" % self.poll.id)

    def tearDown(self):
        self.browser.quit()


    def test_should_show_the_status_page(self):
        self.assertTrue(self.browser.is_element_present_by_css("div[id=poll-status]"))
        self.assertTrue(str(self.poll.id) in self.browser.find_by_css("div[id=poll-status]").text)

        self.assertEqual(self.browser.find_by_id('contact-count').text, "2")
        self.assertEqual(self.browser.find_by_id('category-count').text, "3")
        self.assertEqual(self.browser.find_by_id('is-yesno').text, "yes")




