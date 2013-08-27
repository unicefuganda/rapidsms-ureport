from django.contrib.auth.models import Group, User
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Connection, Contact
from poll.models import Poll
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router
from rapidsms.messages import IncomingMessage

ANY_LOCATION_NAME = 'Neverland'


def create_group(group_name):
    group = Group.objects.create(name=group_name)
    return group

def create_user(username, email, group):
    user1 = User.objects.create(username=username, email=email)
    user1.groups.add(group)
    user1.save()
    return user1

def create_contact(name, user, gender, birthdate, language):
    contact = Contact.objects.create(name=name, user=user, gender=gender, birthdate=birthdate, language=language,
                                     reporting_location= Location.objects.create(name=ANY_LOCATION_NAME))
    return contact

def create_connection(identity, contact, backend):
    connection = Connection.objects.create(identity=identity, backend=backend)
    connection.contact = contact
    connection.save()
    return connection

def create_poll(user):
    poll_name = "functional_test"
    question = "from FT with love!"
    poll = Poll.objects.create(name=poll_name, question=question, user=user, type=Poll.TYPE_TEXT)
    return poll

def add_contacts_to_poll(poll, contacts):
    for contact in contacts:
        poll.contacts.add(contact)
    poll.save()

def create_fake_response(connection, incoming_message):
    router = get_router()
    incoming = router.handle_incoming(connection.backend.name, connection.identity, incoming_message)
    return incoming

def get_incoming_message(connection, message):
    incoming_message = IncomingMessage(connection, message)
    incoming_message.db_message = Message.objects.create(direction='I', connection=connection, text=message)
    return incoming_message
