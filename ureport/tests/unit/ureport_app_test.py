# coding=utf-8
from django.conf import settings
from rapidsms.models import Backend, Connection
from script.models import ScriptProgress
from ureport.models.tests.model_tests import UreportMessagesTestCase


class UrpeortAppTest(UreportMessagesTestCase):
    fixtures = ['test_fix.json', '0004_migration_initial_data.json', 'luo_translation.json', 'script2.json',
                'script_luo.json', 'ussd.json']

    def test_ureport_app_starts_registration_for_users_who_send_the_correct_opt_in_words(self):
        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='0783010831', backend=self.backend)

        opt_in_word = 'join'
        settings.OPT_IN_WORDS = ["enter", "join", "login"]

        self.fakeIncoming(opt_in_word, self.connection)

        self.assertEquals(
            (ScriptProgress.objects.filter(script__slug="ureport_autoreg2", connection=self.connection)).exists(),
            True)

    def test_ureport_app_does_not_start_registration_for_users_who_send_the_wrong_opt_in_word(self):
        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='0783010831', backend=self.backend)

        wrong_op_in_word = 'wrong'
        settings.OPT_IN_WORDS = ["enter", "join", "login"]

        self.fakeIncoming(wrong_op_in_word, self.connection)

        self.assertEquals(
            (ScriptProgress.objects.filter(script__slug="ureport_autoreg2", connection=self.connection)).exists(),
            False)

    def test_ureport_app_starts_registration_for_users_who_send_the_correct_opt_in_words_in_arabic(self):
        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='0783010831', backend=self.backend)

        opt_in_word = 'انضم'
        settings.OPT_IN_WORDS = ["دخول", "انضم", "دخول"]

        self.fakeIncoming(opt_in_word, self.connection)

        self.assertEquals(
            (ScriptProgress.objects.filter(script__slug="ureport_autoreg2", connection=self.connection)).exists(),
            True)