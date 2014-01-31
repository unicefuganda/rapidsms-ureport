import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Contact, Backend, Connection
from script.models import ScriptProgress, Script, ScriptStep, ScriptSession
from ureport.views.api.currentpoll import ViewCurrentPoll


class CurrentPollTest(TestCase):
    def setUp(self):
        self.view = ViewCurrentPoll()

    def test_that_it_retrieves_data_from_poll_when_contact_has_a_poll(self):
        contact, contact_created = Contact.objects.get_or_create(name='John Jonny')
        user, user_created = User.objects.get_or_create(username="test_user")
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        poll, poll_created = Poll.objects.get_or_create(name="Test Poll", question="Is working?", user=user,
                                                        start_date=an_hour_ago)
        poll.contacts = [contact]
        poll.save()
        current_poll = self.view.get_current_poll_for(contact)
        self.assertEqual("Test Poll", current_poll["name"])
        self.assertEqual("Is working?", current_poll["question"])

    def test_that_it_retrieves_data_from_active_poll(self):
        contact, contact_created = Contact.objects.get_or_create(name='John Jonny')
        user, user_created = User.objects.get_or_create(username="test_user")
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        two_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=2)
        thirty_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=30)

        poll, poll_created = Poll.objects.get_or_create(name="Test Poll", question="Is working?", user=user,
                                                        start_date=two_hours_ago)
        second_poll, poll_created = Poll.objects.get_or_create(name="Test Poll 2", question="Is working 2 ?", user=user,
                                                               start_date=an_hour_ago, end_date=thirty_minutes_ago)
        third_poll, poll_created = Poll.objects.get_or_create(name="Test Poll 3", question="Is working 3 ?", user=user)
        poll.contacts = [contact]
        poll.save()

        second_poll.contacts = [contact]
        second_poll.save()

        third_poll.contacts = [contact]
        third_poll.save()
        current_poll = self.view.get_current_poll_for(contact)
        self.assertEqual("Test Poll", current_poll["name"])
        self.assertEqual("Is working?", current_poll["question"])

    def test_that_retrieves_none_when_contact_do_not_have_a_poll(self):
        contact = Contact()
        contact.save()
        self.assertEqual(None, self.view.get_current_poll_for(contact))

    def test_that_gets_the_progress_object_for_ureport_autoreg2(self):
        backend = Backend.objects.create(name="test_backend")
        connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        first_script_progress = ScriptProgress.objects.create(connection=connection, script=script)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg")
        second_script_progress = ScriptProgress.objects.create(connection=connection, script=script)
        self.assertEqual(first_script_progress, self.view.get_script_progress(connection))

    def test_that_returns_new_script_progress_if_connection_is_not_associated_to_script_progress(self):
        script_autoreg2, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        backend = Backend.objects.create(name="test_backend")
        connection = Connection.objects.create(identity="7777", backend=backend)
        second_connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="other_script")
        first_step = ScriptStep.objects.create(script=script_autoreg2, order=1)
        second_step = ScriptStep.objects.create(script=script_autoreg2, order=2)
        script_progress = ScriptProgress.objects.create(connection=connection, script=script)
        self.assertEqual("ureport_autoreg2", self.view.get_script_progress(connection).script.slug)
        script_session_list = ScriptSession.objects.filter(script=script_autoreg2, connection=connection)
        self.assertEqual(1, len(script_session_list))

    def test_that_raise_exception_if_script_ureport_autoreg2_does_not_exist(self):
        backend = Backend.objects.create(name="test_backend")
        connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg")
        with self.assertRaises(Script.DoesNotExist):
            self.view.get_script_progress(connection)

    def test_that_retrieves_same_step_for_script_progress_that_is_in_progress(self):
        view = ViewCurrentPoll()
        backend = Backend.objects.create(name="test_backend")
        connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        first_step = ScriptStep.objects.create(script=script, order=1)
        second_step = ScriptStep.objects.create(script=script, order=2)
        third_step = ScriptStep.objects.create(script=script, order=3)
        script_progress = ScriptProgress.objects.create(connection=connection, script=script, step=second_step)

        self.assertEqual(second_step, view.get_current_step(script_progress))

    def test_that_retrieves_last_step_for_a_script_progress_that_is_in_last_step(self):
        view = ViewCurrentPoll()
        backend = Backend.objects.create(name="test_backend")
        connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        first_step = ScriptStep.objects.create(script=script, order=1)
        second_step = ScriptStep.objects.create(script=script, order=2)
        third_step = ScriptStep.objects.create(script=script, order=3)
        script_progress = ScriptProgress.objects.create(connection=connection, script=script, step=third_step)

        self.assertEqual(third_step, view.get_current_step(script_progress))
