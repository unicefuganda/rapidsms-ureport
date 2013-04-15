import datetime
from uganda_common.utils import previous_calendar_week
from uganda_common.utils import previous_calendar_month
from uganda_common.utils import previous_calendar_quarter
from django.test import TestCase


class CalendarUtilsTest(TestCase):

    # All functions being tested here seem to be unused elsewhere in the code

    def test_should_calculate_first_day_of_previous_week_from_now(self):
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=7)

        returned = previous_calendar_week()
        returned_start_date = returned[0].date()
        returned_end_date = returned[1].date()

        self.assertEquals((returned_start_date, returned_end_date), (start_date, end_date))

    def test_should_calculate_first_day_of_previous_month_from_now(self):
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=30)

        returned_tuple = previous_calendar_month()
        returned_start_date = returned_tuple[0].date()
        returned_end_date = returned_tuple[1].date()

        self.assertEquals((returned_start_date, returned_end_date), (start_date, end_date))

    def test_should_calculate_first_day_of_previous_quarter_from_now(self):
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=90)

        returned_tuple = previous_calendar_quarter()
        returned_start_date = returned_tuple[0].date()
        returned_end_date = returned_tuple[1].date()

        self.assertEquals((returned_start_date, returned_end_date), (start_date, end_date))

