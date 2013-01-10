from rapidsms.contrib.locations.models import Location
import xlwt
from uganda_common.utils import create_workbook

def _get_data(response):
    location = response.contact.reporting_location
    location_name = '' if location is None else location.name
    return [response.message.connection.identity, response.contact.name,
            location_name, response.message.text]


def get_poll_responses(poll):
    return [_get_data(response) for response in poll.responses.all()]


def get_excel_dump_report_for_poll(poll):
    poll_responses = get_poll_responses(poll)

    headers = ['Phone Number', 'Name', 'Location', 'Message']
    poll_responses.insert(0, headers)

    return create_workbook(data=poll_responses, encoding='utf8')
