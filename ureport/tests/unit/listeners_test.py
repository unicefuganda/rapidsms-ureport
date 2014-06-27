from unittest import TestCase
from ureport.models.database_views import UreportContact
from ureport.models.litseners import check_location_length


class ListenersTest(TestCase):

    def setUp(self):
        self.max_village_length = UreportContact.MAX_VILLAGE_LENGTH

    def tearDown(self):
        UreportContact.MAX_VILLAGE_LENGTH = self.max_village_length

    def test_that_check_location_length_retrieves_the_location_when_length_is_not_greater_than_the_limit(self):
        UreportContact.MAX_VILLAGE_LENGTH = 10
        location = 'Kampala'
        self.assertEquals(location, check_location_length(location))


    def test_that_check_location_length_retrieves_empty_string_when_is_greater_than_the_limit(self):
        UreportContact.MAX_VILLAGE_LENGTH = 5
        location = 'Kampala value'
        self.assertEquals('value', check_location_length(location))