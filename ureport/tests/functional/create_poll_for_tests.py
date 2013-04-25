from datetime import datetime
import time
from rapidsms.models import Contact,Connection, Backend
from ureport.tests.functional.create_poll_utils import create_group, create_user, create_connection, create_poll,\
    add_contacts_to_poll
from poll.models import Poll


def start_poll_queues_messages_in_table(driver):

    group = create_group(group_name='groupFT')
    user1 = create_user(username="foo",email='foo@bar.com', group=group)
    user2 = create_user(username='fred', email='shaggy@scooby.com', group=group)

    contact1 = Contact.objects.create(pk=999, name='FT1', user=user1, gender='M', birthdate=datetime.now(), language="en")
    contact2 = Contact.objects.create(pk=1000, name='FT2', user=user2, gender='M', birthdate=datetime.now(), language="en")
    contacts = [contact1, contact2]

    backend = Backend.objects.create(name='test_backend')
    create_connection(identity='0794339344', contact=contact1, backend=backend)
    create_connection(identity='0794339427', contact=contact2, backend=backend)

    poll = create_poll(user2)
    add_contacts_to_poll(poll, contacts)

    driver.create_and_sign_in_admin("argha", "a")

    driver.open("/view_poll/%s" % poll.id)
    driver.browser.find_link_by_text('Start Poll').first.click()

    assert driver.browser.is_text_present('Close Poll')

    return poll.id, poll.contacts.count()
