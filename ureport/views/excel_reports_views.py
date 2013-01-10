from datetime import date
from time import strftime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ureport.spreadsheet_utils import get_excel_dump_report_for_poll
from poll.models import Poll

@login_required
def generate_poll_dump_report(request, poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
        book = get_excel_dump_report_for_poll(poll)
        response = HttpResponse(mimetype="application/vnd.ms-excel")
        fname_prefix = date.today().strftime('%Y%m%d') + "-" + strftime('%H%M%S')
        response["Content-Disposition"] = 'attachment; filename=%s_poll_%s_dump_report.xls' % (fname_prefix,poll_id)
        book.save(response)
        return response
    except Poll.DoesNotExist:
        return HttpResponse('Sorry, the poll does not exist')

