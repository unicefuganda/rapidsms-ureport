from datetime import datetime
from rapidsms.models import Backend
from rapidsms_ureport.ureport.tests.functional.create_poll_utils import create_group, create_user, create_connection, create_poll, add_contacts_to_poll, create_contact
from django.contrib.auth.models import User


def start_poll_queues_messages_in_table():

    group = create_group(group_name='groupFT')
    user1 = create_user(username="foo",email='foo@bar.com', group=group)
    user2 = create_user(username='fred', email='shaggy@scooby.com', group=group)

    contact1 = create_contact(name='FT1', user=user1, gender='M', birthdate=datetime.now(), language="en")
    contact2 = create_contact(name='FT1', user=user2, gender='M', birthdate=datetime.now(), language="en")
    contacts = [contact1, contact2]

    backend = Backend.objects.create(name='test_backend')
    connections_list = []
    connections_list.append(create_connection(identity='0794339344', contact=contact1, backend=backend))
    connections_list.append(create_connection(identity='0794339427', contact=contact2, backend=backend))

    poll = create_poll(User.objects.all()[0])

    poll.add_yesno_categories()
    poll.save()

    add_contacts_to_poll(poll, contacts)

    return poll, connections_list

