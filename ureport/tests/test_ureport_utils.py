from unittest import TestCase
from django.contrib.auth.models import User
from rapidsms_polls.poll.models import Poll
from rapidsms_script.script.models import Script, ScriptStep
from rapidsms_ureport.ureport.utils import configure_messages_for_script


class TestUreportUtils(TestCase):

    def setUp(self):
        self.script_name = 'test_change_registration_script_messages'
        self.script = Script.objects.create(slug=self.script_name)
        self.poll_user = User.objects.create(username="test_reg_messages_user", email='foo@foo.com')

    def tearDown(self):
        ScriptStep.objects.all().delete()
        Script.objects.all().delete()
        User.objects.get(username="test_reg_messages_user").delete()
        Poll.objects.all().delete()

    def test_should_update_scripts_that_have_messages(self):
        #given
        ScriptStep.objects.create(script=self.script,order=0,message='foo0')
        ScriptStep.objects.create(script=self.script,order=1,message='foo1')
        ScriptStep.objects.create(script=self.script,order=2,message='foo2')
        ScriptStep.objects.create(script=self.script,order=3,message='foo3')

        message_dict = {0:'bar0',1:'bar1', 2:'bar2', 3:'bar3'}

        #when
        configure_messages_for_script(self.script_name, message_dict)

        #then
        script = Script.objects.get(slug=self.script_name)
        script_steps = script.steps.order_by('order')

        self.assertEquals(script_steps[0].message, message_dict.get(0) )
        self.assertEquals(script_steps[1].message, message_dict.get(1) )
        self.assertEquals(script_steps[2].message, message_dict.get(2))
        self.assertEquals(script_steps[3].message, message_dict.get(3))

    def test_should_update_scripts_that_have_poll_questions(self):
        poll1 = Poll.objects.create(name="foo_poll1", question='test_registration_messages_poll_question1', type=Poll.TYPE_TEXT, user=self.poll_user)
        poll2 = Poll.objects.create(name="foo_poll2", question='test_registration_messages_poll_question2', type=Poll.TYPE_TEXT, user=self.poll_user)

        ScriptStep.objects.create(script=self.script,order=0,poll=poll1)
        ScriptStep.objects.create(script=self.script,order=1,poll=poll2)

        message_dict = {0:'changed_poll_question_for_order0',1:'changed_poll_question_for_order1'}

        configure_messages_for_script(self.script_name,message_dict)

        script = Script.objects.get(slug=self.script_name)
        script_steps = script.steps.order_by('order')

        self.assertEquals(script_steps[0].poll.question, message_dict.get(0))
        self.assertEquals(script_steps[1].poll.question, message_dict.get(1))

    def test_should_update_scripts_that_have_both_message_and_poll(self):
        poll1 = Poll.objects.create(name="foo_poll1", question='test_registration_script_with_message_and_poll_question1', type=Poll.TYPE_TEXT, user=self.poll_user)
        poll2 = Poll.objects.create(name="foo_poll2", question='test_registration_script_with_message_and_poll_question2', type=Poll.TYPE_TEXT, user=self.poll_user)

        ScriptStep.objects.create(script=self.script,order=0,message='test_registration_message1')
        ScriptStep.objects.create(script=self.script,order=1, message='test_registration_message1')
        ScriptStep.objects.create(script=self.script,order=2, poll=poll1)
        ScriptStep.objects.create(script=self.script,order=3, poll=poll2)

        message_dict = {0:'changed_to_message1',1:'changed_to_message2'}

        configure_messages_for_script(self.script_name, message_dict)

        script = Script.objects.get(slug=self.script_name)
        script_steps = script.steps.order_by('order')

        self.assertEquals(script_steps[0].message, message_dict.get(0))
        self.assertEquals(script_steps[1].message, message_dict.get(1))
        self.assertEquals(script_steps)

    def test_should_raise_exception_if_there_is_no_script(self):
        self.assertRaises(Script.DoesNotExist,configure_messages_for_script("should_fail", {}))