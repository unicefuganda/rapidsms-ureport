from rapidsms.contrib.locations.models import Location
from uganda_common.utils import create_workbook
from geoserver.models import PollData

def get_excel_dump_report_for_poll(poll):
    poll_responses = get_poll_responses(poll)

    headers = ['Phone Number', 'Name', 'Location', 'Message']
    poll_responses.insert(0, headers)

    return create_workbook(data=poll_responses, encoding='utf8')

def get_per_district_excel_report_for_yes_no_polls(poll_id):
    poll_responses = get_formatted_responses_for_poll_per_district(poll_id)
    return create_workbook(data=poll_responses, encoding='utf8')


def _get_data(response):
    location = response.contact.reporting_location
    location_name = '' if location is None else location.name
    return [response.message.connection.identity, response.contact.name,
            location_name, response.message.text]


def get_poll_responses(poll):
    return [_get_data(response) for response in poll.responses.all()]


def get_formatted_responses_for_poll_per_district(poll_id):
    from django.db import connections
    cursor = connections['geoserver'].cursor()
    q = 'select district, yes*100, no*100, (unknown+uncategorized)*100'+\
        ' from geoserver_polldata where poll_id=' + str(poll_id)
    cursor.execute(q)
    poll_responses = cursor.fetchall()
    headers = ['District', 'Yes(%)', 'No(%)', 'Unknown(%)']
    poll_responses.insert(0, headers)
    return poll_responses

