from unittest import TestCase
from ureport_project import settings
from ureport_project.rapidsms_ureport.ureport.context_processors import has_valid_pagination_limit


class ContextProcessorTest(TestCase):

    def tearDown(self):
        self.clear_settings()

    def test_should_not_have_valid_pagination_limit_if_settings_are_not_present(self):
        self.clear_settings()
        self.assertFalse(has_valid_pagination_limit(settings))

    def test_should_fail_if_pagination_limit_is_not_a_number(self):
        settings.PAGINATION_LIMIT = 'text'
        self.assertFalse(has_valid_pagination_limit(settings))

    def test_should_pass_if_pagination_limit_in_settings_is_a_number(self):
        settings.PAGINATION_LIMIT = 10
        self.assertTrue(has_valid_pagination_limit(settings))

    def clear_settings(self):
        try:
            return delattr(settings, 'PAGINATION_LIMIT')
        except AttributeError:
            pass

