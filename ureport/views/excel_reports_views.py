from datetime import date
from time import strftime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from ureport.spreadsheet_utils import get_excel_dump_report_for_poll, \
    get_per_district_excel_report_for_yes_no_polls
from poll.models import Poll
from ureport.forms import UploadContactsForm, AssignGroupForm


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

@login_required
def generate_per_district_report(request, poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
    except Poll.DoesNotExist:
        return HttpResponse('Sorry, the poll does not exist')
    if poll.is_yesno_poll():
        book = get_per_district_excel_report_for_yes_no_polls(poll_id)
        response = HttpResponse(mimetype="application/vnd.ms-excel")
        fname_prefix = date.today().strftime('%Y%m%d') + "-" + strftime('%H%M%S')
        response["Content-Disposition"] = 'attachment; filename=%s_poll_%s_dump_report.xls' % (fname_prefix,poll_id)
        book.save(response)
        return response
    return HttpResponse('Sorry, the poll is not yes-no type')


@login_required
@never_cache
def upload_users(request):
    form = UploadContactsForm()
    if request.method == 'POST':
        form = UploadContactsForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()
            UploadContactsForm.process(upload)
            return HttpResponseRedirect(reverse('upload_users'))
    return render_to_response('ureport/upload_users.html', locals(), context_instance=RequestContext(request))


@login_required
def assign_group(request):
    form = AssignGroupForm()
    if request.method == 'POST':
        form = AssignGroupForm(request.POST, request.FILES)
        if form.is_valid():
            path = form.handle_upload(request.FILES['contacts'])
            form.process(path, request.user.username)
            return HttpResponseRedirect(reverse("assign_group"))
    return render_to_response('ureport/upload_users.html', locals(), context_instance=RequestContext(request))