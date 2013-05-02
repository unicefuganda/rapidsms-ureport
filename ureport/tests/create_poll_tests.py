from django.test import TestCase
from ureport.forms import NewPollForm

__author__ = 'kenneth'


class CreatePollTest(TestCase):

    def test_clean_default_response(self):
        form = NewPollForm()
        value = '91% of Ugandans voted in favor of Sevo'
        end_value = '91%% of Ugandans voted in favor of Sevo'
        self.assertEqual(form._cleaned_default_response(value), end_value)