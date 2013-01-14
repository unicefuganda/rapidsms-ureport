from rapidsms.contrib.locations.models import Location
from uganda_common.utils import create_workbook
from geoserver.models import PollData

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


def _get_formatted_data(response):
    response_unknown = response.uncategorized + response.unknown
    return response.district, response.yes+response.no+response_unknown, \
           response.yes, response.no,\
           response_unknown


def get_formatted_responses_for_poll_per_district(poll_id):
    poll_responses_by_district = PollData.objects.using('geoserver').filter(poll_id=poll_id)
    poll_responses = [_get_formatted_data(response) for response in poll_responses_by_district]
    headers = ['District', 'Total received', 'Yes', 'No', 'Unknown']
    poll_responses.insert(0, headers)
    return poll_responses


def get_per_district_excel_report_for_yes_no_polls(poll_id):
    poll_responses = get_formatted_responses_for_poll_per_district(poll_id)
    return create_workbook(data=poll_responses, encoding='utf8')
