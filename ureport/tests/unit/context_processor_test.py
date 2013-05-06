from unittest import TestCase
from fixtures.create_polls_for_view_poll import create_and_start_polls
from ureport_project import settings
from ureport_project.rapidsms_ureport.ureport.context_processors import has_valid_pagination_limit


class ContextProcessorTest(TestCase):

    def test_should_fail_if_pagination_limit_does_not_exist_in_settings(self):
        modified_settings = settings.__dict__.pop('PAGINATION_LIMIT')
        self.assertFalse(has_valid_pagination_limit(modified_settings))

    def test_should_fail_if_pagination_limit_is_no_a_number(self):
        bad_settings = settings.__dict__['PAGINATION_LIMIT'] = 'text'
        self.assertFalse(has_valid_pagination_limit(bad_settings))

    def test_should_pass_if_pagination_limit_in_settings_is_a_number(self):
        settings.PAGINATION_LIMIT = 10
        good_settings = settings
        self.assertTrue(has_valid_pagination_limit(good_settings))
