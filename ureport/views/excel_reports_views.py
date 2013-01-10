from datetime import date
from time import strftime
from django.http import HttpResponse
from ureport.spreadsheet_utils import get_excel_dump_report_for_poll
from poll.models import Poll


def generate_poll_dump_report(request, poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
        book = get_excel_dump_report_for_poll(poll)
        response = HttpResponse(mimetype="application/vnd.ms-excel")
        fname_prefix = date.today().strftime('%Y%m%d') + "-" + strftime('%H%M%S')
        response["Content-Disposition"] = 'attachment; filename=%s_%s_dump_report.xls' % (fname_prefix,
                                                                                          poll.name)
        book.save(response)
        return response
    except Poll.DoesNotExist:
        return HttpResponse('Sorry, the poll does not exist')

