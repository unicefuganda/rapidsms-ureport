from datetime import datetime
from django.contrib.auth.models import User, Group
from poll.models import Poll
from rapidsms.models import Contact,Connection, Backend

def create_poll(driver, poll_name, question, group_name):
    driver.open('/createpoll/')
    driver.browser.fill("name", "%s" % poll_name)
    driver.browser.fill("question_en", question)
    driver.select_by_text('groups', group_name)
    driver.browser.find_by_id('createPoll').click()


def start_poll_queues_messages_in_table(driver):
    group_name = 'groupFT'
    group = Group.objects.create(name=group_name)
    user1 = User.objects.create(username="foo", email='foo@bar.com')
    user1.groups.add(group)
    user1.save()

    user2 = User.objects.create(username='fred', email='shaggy@scooby.com')
    user2.groups.add(group)
    user2.save()

    contact1 = Contact.objects.create(pk=999, name='FT1', user=user1, gender='M',birthdate=datetime.now(),language="en")
    contact2 = Contact.objects.create(pk=1000, name='FT2', user=user2, gender='M',birthdate=datetime.now(),language="en")

    backend = Backend.objects.create(name='test_backend')

    conn1 = Connection.objects.create(identity='0794339344', backend=backend)
    conn1.contact = contact1
    conn1.save()

    conn2 = Connection.objects.create(identity='0794339427', backend=backend)
    conn2.contact = contact2
    conn2.save()

    poll_name = "functional_test"
    question = "from FT with love!"
    poll = Poll.objects.create(name=poll_name, question=question, user=user2, type=Poll.TYPE_TEXT)
    poll.contacts.add(contact1)
    poll.contacts.add(contact2)
    poll.save()


    # create_poll(driver,poll_name,question,group_name)

    driver.create_and_sign_in_admin("argha","a")

    driver.open("/view_poll/%s" % poll.id)
    driver.browser.find_link_by_text('Start Poll').first.click()

    assert driver.browser.is_text_present('Close Poll')

    return poll.id,poll.contacts.count()
