from datetime import datetime
from django.contrib.auth.models import Group, User
from rapidsms.models import Connection, Contact, Backend
from poll.models import Poll
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router


def create_group(group_name):
    group = Group.objects.create(name=group_name)
    return group


def create_user(username, email, group):
    user1 = User.objects.create(username=username, email=email)
    user1.groups.add(group)
    user1.save()
    return user1


def create_connection(identity, contact, backend):
    connection = Connection.objects.create(identity=identity, backend=backend)
    connection.contact = contact
    connection.save()
    return connection

def create_poll(contacts, user):
    poll_name = "functional_test"
    question = "from FT with love!"
    poll = Poll.objects.create(name=poll_name, question=question, user=user, type=Poll.TYPE_TEXT)
    for contact in contacts:
        poll.contacts.add(contact)
    poll.save()
    return poll


def fake_incoming(connection, incoming_message):
    router = get_router()
    return router.handle_incoming(connection.backend.name, connection.identity, incoming_message)


def create_eleven_polls_for_view_polls():
    group = create_group(group_name='Pagination Group')
    user1 = create_user(username="foo", email='foo@bar.com', group=group)
    user2 = create_user(username='fred', email='shaggy@scooby.com', group=group)

    contact1 = Contact.objects.create(pk=567, name='FT1', user=user1, gender='M', birthdate=datetime.now(),
                                      language="en")
    contact2 = Contact.objects.create(pk=765, name='FT2', user=user2, gender='M', birthdate=datetime.now(),
                                      language="en")
    contacts = [contact1,contact2]

    backend = Backend.objects.create(name='dmark')

    connection1 = create_connection('0794339344', contact1, backend)
    connection2 = create_connection('0794339427', contact2, backend)
    connections = [connection1, connection2]

    polls = []
    for poll in range(0, 10):
        poll = create_poll(contacts, user1)
        poll.add_yesno_categories()
        polls.append(poll)

        for connection in connections:
            fake_incoming(connection, 'yes')

    return polls