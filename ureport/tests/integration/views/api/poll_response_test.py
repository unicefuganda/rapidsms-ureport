import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Contact, Backend, Connection
from script.models import Script, ScriptStep, ScriptProgress, ScriptSession
from ureport.views.api.poll_responses import SubmitPollResponses


class SubmitPollResponseTest(TestCase):
    def setup_poll(self, default_response=""):
        user, user_created = User.objects.get_or_create(username="test_user")
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        poll, poll_created = Poll.objects.get_or_create(name="Test Poll", question="Is working?", user=user,
                                                        start_date=an_hour_ago, default_response=default_response)
        return poll

    def test_process_poll_returns_an_outgoing_message(self):
        backend = Backend.objects.create(name="test_backend")
        connection = Connection.objects.create(identity="7777", backend=backend)
        contact, contact_created = Contact.objects.get_or_create(name='John Jonny')
        connection.contact = contact
        connection.save()
        script = Script.objects.create(slug="who")
        ScriptSession.objects.create(connection=connection, script=script)
        default_response = "Thanks"
        poll = self.setup_poll(default_response)
        view = SubmitPollResponses()
        view.connection = connection
        accepted, outgoing_message = view.process_poll_response("Yes", poll)
        self.assertEqual(True, accepted)
        self.assertEqual(default_response, outgoing_message)

    def test_that_get_script_progress_for_poll_returns_none_if_there_is_no_script_progress_for_the_poll(self):
        poll = self.setup_poll()
        view = SubmitPollResponses()
        backend = Backend.objects.create(name="test_backend")
        view.connection = Connection.objects.create(identity="7777", backend=backend)
        script_progress = view.get_script_progress_for_poll(poll)
        self.assertEqual(None, script_progress)

    def test_that_get_script_progress_for_poll_returns_script_progress(self):
        poll = self.setup_poll()
        view = SubmitPollResponses()
        backend = Backend.objects.create(name="test_backend")
        view.connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        ScriptStep.objects.create(script=script, order=1, poll=poll)
        script_progress = ScriptProgress.objects.create(connection=view.connection, script=script)
        script_progress.start()
        self.assertEqual(script_progress, view.get_script_progress_for_poll(poll))

    def test_that_that_script_progress_moves_to_next_step_if_exists(self):
        poll = self.setup_poll()
        view = SubmitPollResponses()
        backend = Backend.objects.create(name="test_backend")
        view.connection = Connection.objects.create(identity="7777", backend=backend)
        script, created = Script.objects.get_or_create(slug="ureport_autoreg2")
        ScriptStep.objects.create(script=script, order=1, poll=poll)
        ScriptStep.objects.create(script=script, order=2, message="")
        script_progress = ScriptProgress.objects.create(connection=view.connection, script=script)
        script_progress.start()
        view.process_registration_steps(poll)
        reloaded_script_progress = ScriptProgress.objects.get(pk=script_progress.id)
        self.assertEqual(2, reloaded_script_progress.step.order)

