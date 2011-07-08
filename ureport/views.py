from django.shortcuts import  render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.db.models import Q, Manager
from django import forms
from django.contrib.auth.models import Group
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from ureport.settings import colors, drop_words, tag_cloud_size
from ureport.models import IgnoredTags
from poll.models import *

from rapidsms.models import Contact, Connection
from rapidsms_httprouter.router import get_router, start_sending_mass_messages, stop_sending_mass_messages
from rapidsms_httprouter.views import receive
from djtables import Column, Table
from djtables.column import DateColumn
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms_httprouter.models import Message, DIRECTION_CHOICES, STATUS_CHOICES

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.datastructures import SortedDict

from generic.views import generic, generic_dashboard

from .models import MassText
from .forms import EditReporterForm, ReplyForm
from .utils import retrieve_poll
from ureport.forms import *
from generic.forms import StaticModuleForm
from generic.models import Dashboard
from django.forms import forms
from django.core.files import File
from xlrd import open_workbook
from uganda_common.utils import assign_backend
from ureport.models import find_closest_match
from django.views.decorators.cache import cache_control

import re
import bisect
import textwrap
import random
import datetime

TAG_CLASSES=['tag1','tag2','tag3','tag4','tag5','tag6','tag7']

def generate_tag_cloud(words,counts_dict,tag_classes,max_count):
    """
        returns tag words with assosiated tag classes depending on their frequency
    @params:
             words: a dictionary of words and their associated counts
             counts_dict: a dictionary of counts and their associated words
             tag_classes: a list of tag classes sorted minumum to max
            max_count:the maximum frequency of the tag words
            """
    tags=[]
    used_words_list=[]
    divisor = (tag_cloud_size / len(tag_classes)) + 1
    for i in range(max_count,0,-1):
        for word in counts_dict[i]:
            if not word in used_words_list:
                k={}
                klass=tag_classes[len(tags)/divisor]
                k['tag']=word
                k['class']=klass
                tags.append(k)
                used_words_list.append(word)
                if (len(used_words_list)==tag_cloud_size):
                    return tags

    return tags

@login_required
def add_drop_word(request, tag_name=None, poll_pk=None):
    tag_name=tag_name if tag_name != None else request.GET.get('tag',None)
    poll_pk= poll_pk if poll_pk != None else int(request.GET.get('poll',1))
    print "Adding ignored tag %s to %d" % (tag_name, poll_pk)
    IgnoredTags.objects.create(name=tag_name,poll=Poll.objects.get(pk=poll_pk))
    return HttpResponse(simplejson.dumps("success"))

@login_required
def delete_drop_word(request):
    tag_name=request.GET.get('tag',None)
    tags=IgnoredTags.objects.filter(name=tag_name)
    for tag in tags:
        tag.delete()
    return HttpResponse(simplejson.dumps("success"))

@login_required
@cache_control(no_cache=True, max_age=0)
def show_ignored_tags(request, poll_id):
    tags=IgnoredTags.objects.all()
    return render_to_response("ureport/partials/tag_cloud/ignored_tags.html", {'tags':tags, 'tag_poll_pk':poll_id},context_instance=RequestContext(request))

def _get_tags(polls):
    responses=Response.objects.filter(poll__in=polls)
    words=''
    word_count={}
    counts_dict={}
    used_words_list=[]
    max_count=0
    reg_words = re.compile('[^a-zA-Z]')
    print "ignored tags = %s" % str(list(IgnoredTags.objects.filter(poll__in=polls).values_list('name',flat=True)))
    dropwords = list(IgnoredTags.objects.filter(poll__in=polls).values_list('name',flat=True)) + drop_words 
    all_words = ' '.join(Value.objects.filter(entity_ct=ContentType.objects.get_for_model(Response), entity_id__in=responses).values_list('value_text', flat=True)).lower()
    all_words = reg_words.split(all_words)
    #poll question
    poll_qn=['Qn:'+' '.join(textwrap.wrap(poll.question.rsplit('?')[0]))+'?' for poll in polls]
    for d in dropwords:
        drop_word = d.lower()
        while True:
            try:
                all_words.remove(drop_word)
            except ValueError:
                break

    for word in all_words:
        if len(word) >2:
            word_count.setdefault(word,0)
            word_count[word]+=1
            counts_dict.setdefault(word_count[word],[])
            counts_dict[word_count[word]].append(word)

            if word_count[word]>max_count:
                max_count=word_count[word]

    tags=generate_tag_cloud(word_count,counts_dict,TAG_CLASSES,max_count)
    #randomly shuffle tags
    random.shuffle(tags)
    return tags

@cache_control(no_cache=True, max_age=0)
def tag_cloud(request, pks):
    """
        generates a tag cloud
    """
    polls = retrieve_poll(request, pks)

    poll_qn=['Qn:'+' '.join(textwrap.wrap(poll.question.rsplit('?')[0]))+'?' for poll in polls]

    tags = _get_tags(polls) 
    return render_to_response("ureport/partials/tag_cloud/tag_cloud.html", {'poll':polls[0],'tags':tags,'poll_qn':poll_qn[0], 'poll_id':pks}, context_instance=RequestContext(request))

def histogram(request):
    """
         view for numeric polls
    """

    all_polls=Poll.objects.filter(type=u'n')
    if request.GET.get('pks', None):
        items=6
        polls = retrieve_poll(request)
        responses=Response.objects.filter(poll__in=polls)
        pks = polls.values_list('pk', flat=True)
        responses=Response.objects.filter(poll__in=polls,poll__type=u'n')
        plottable_data={}
        if responses:
            poll_results={}
            poll_qns=['Qn:'+poll.question+'<br>' for poll in Poll.objects.filter(pk__in=pks)]

            total_responses=responses.count()
            vals_list=Value.objects.filter(entity_id__in=responses).values_list('value_float',flat=True)
            vals_list=sorted(vals_list)
            max=int(vals_list[-1])
            min=int(vals_list[0])
            num_list=range(min,max)
            increment=int(max/items)
            bounds=num_list[::increment]
            ranges_list=[str(a)+'-'+str(a+increment) for a in bounds if a<max]
            poll_results['categories']=ranges_list
            poll_results['title']=poll_qns

            for response in responses:
                name=response.poll.name
                poll_results.setdefault(name,{})
                poll_results[name].setdefault('data',{})
                if len(response.eav_values.all())>0:
                    value=int(response.eav_values.all()[0].value_float)
                pos=bisect.bisect_right(bounds,value)-1
                r=ranges_list[pos]
                poll_results[name]['data'].setdefault(r,0)
                poll_results[name]['data'][r]+=1

            data=[]
            for key in poll_results.keys():
                if key  not in ['categories','title']:
                    d={}
                    d['name']=key
                    d['data'] =poll_results[key]['data'].values()
                    data.append(d)
            plottable_data['data']=data
            plottable_data['title']  =poll_qns
            plottable_data['categories'] =ranges_list
            plottable_data['mean'] =sum(vals_list)/len(vals_list)
            plottable_data['median']=vals_list[len(vals_list)/2]
        return HttpResponse(mark_safe(simplejson.dumps(plottable_data)) )

    return render_to_response("ureport/histogram.html", {'polls':all_polls}, context_instance=RequestContext(request))

@login_required
def view_message_history(request, connection_id):
    """
        This view lists all (sms message) correspondence between 
        RapidSMS and a User 
        
    """
    direction_choices   = DIRECTION_CHOICES
    status_choices      = STATUS_CHOICES
    reply_form = ReplyForm()
    connection = get_object_or_404(Connection, pk=connection_id)

    if connection.contact:
        messages = Message.objects.filter(connection__contact=connection.contact)
    else:
        messages = Message.objects.filter(connection=connection)
    messages = messages.order_by('-date')

    try:
        latest_message  = messages.filter(direction="I").latest('date')
        total_incoming = messages.filter(direction="I").count()
        total_outgoing = messages.filter(direction="O").count()
    except Message.DoesNotExist:
        messages = []
        latest_message = []
        total_incoming = 0
        total_outgoing = 0

    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            if Connection.objects.filter(identity=reply_form.cleaned_data['recipient']).count():
                text = reply_form.cleaned_data['message']
                conn = Connection.objects.filter(identity=reply_form.cleaned_data['recipient'])[0]
                in_response_to = reply_form.cleaned_data['in_response_to']
                outgoing = OutgoingMessage(conn, text)
                get_router().handle_outgoing(outgoing, in_response_to)
                return redirect("/ureport/%d/message_history/" % connection.pk)
            else:
                reply_form.errors.setdefault('short_description', ErrorList())
                reply_form.errors['recipient'].append("This number isn't in the system")

    return render_to_response("ureport/message_history.html", {
        "messages": messages,
        "stats_latest_message": latest_message,
        "stats_total_incoming": total_incoming,
        "stats_total_outgoing": total_outgoing,
        "connection": connection,
        "direction_choices": direction_choices,
        "status_choices": status_choices,
        "replyForm": reply_form
    }, context_instance=RequestContext(request))

def show_timeseries(request, pks):
    polls = retrieve_poll(request, pks)
    poll_obj= polls[0]
    responses=Response.objects.filter(poll=poll_obj)
    start_date=poll_obj.start_date
    end_date=poll_obj.end_date or datetime.datetime.now()
    poll = poll_obj.question.replace('"', '\\"')
    interval =datetime.timedelta(minutes=60)
    current_date=start_date
    message_count_list=[]
    while current_date<end_date:
        count=responses.filter(message__date__range=(start_date,current_date)).count()
        message_count_list.append(count)
        current_date+=interval

    return render_to_response("ureport/partials/viz/timeseries.html",{'counts':mark_safe(message_count_list),'start':start_date,'end':end_date,'poll':mark_safe(poll)},context_instance=RequestContext(request))

@login_required
def deleteReporter(request, reporter_pk):
    reporter = get_object_or_404(Contact, pk=reporter_pk)
    if request.method == 'POST':
        reporter.delete()
    return HttpResponse(status=200)

@login_required
def editReporter(request, reporter_pk):
    reporter = get_object_or_404(Contact, pk=reporter_pk)
    reporter_form = EditReporterForm(instance=reporter)
    if request.method == 'POST':
        reporter_form = EditReporterForm(instance=reporter,
                data=request.POST)
        if reporter_form.is_valid():
            reporter_form.save()
        else:
            return render_to_response('ureport/partials/contacts/edit_reporter.html'
                    , {'reporter_form': reporter_form, 'reporter'
                    : reporter},
                    context_instance=RequestContext(request))
        return render_to_response('/ureport/partials/contacts/contacts_row.html',
                                  {'object':Contact.objects.get(pk=reporter_pk),
                                   'selectable':True},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('ureport/partials/contacts/edit_reporter.html',
                                  {'reporter_form': reporter_form,
                                  'reporter': reporter},
                                  context_instance=RequestContext(request))

@login_required
def view_responses(req, poll_id):
    poll = get_object_or_404(Poll,pk=poll_id)

    if hasattr(Contact, 'groups'):
        responses = poll.responses.filter(contact__groups__in=req.user.groups.all())
    else:
        responses = poll.responses.all()
    responses = responses.order_by('-date')
    typedef = Poll.TYPE_CHOICES[poll.type]
    columns = [('Sender', False, 'sender', None)]
    for column, style_class in typedef['report_columns']:
        columns.append((column, False, style_class, None))

    return generic(req,
        model=Response,
        queryset=responses,
        objects_per_page=25,
        selectable=False,
        partial_base='ureport/partials/polls/poll_partial_base.html',
        row_base=typedef['view_template'],
        columns=columns,
        partial_row='ureport/partials/polls/response_row.html'
    )

def _get_responses(poll):
    bad_words = getattr(settings, 'BAD_WORDS', [])
    responses = Response.objects.filter(poll=poll)
    for helldamn in bad_words:
        responses = responses.exclude(message__text__icontains=(" %s " % helldamn)).exclude(message__text__istartswith=("%s " % helldamn))
    paginator = Paginator(responses, 8)
    responses = paginator.page(1).object_list
    return responses

def best_visualization(request, poll_id=None):
    module = False
    if 'module' in request.GET:
        module=True
#    polls = retrieve_poll(request, pks)
#    poll = polls[0]
    if poll_id:
        poll = Poll.objects.get(pk=poll_id)
    else:
        poll = Poll.objects.latest('start_date')
    dict = { 'poll':poll, 'polls':[poll], 'unlabeled':True, 'module':module }
    if poll.type == Poll.TYPE_TEXT and ResponseCategory.objects.filter(response__poll=poll).count() == 0:
        dict.update({'tags':_get_tags([poll]), 'responses':_get_responses(poll)})
    return render_to_response(\
        "/ureport/partials/viz/best_visualization.html",
        dict,
        context_instance=RequestContext(request))

def ureport_content(request, slug, base_template='ureport/two-column.html',**kwargs):
    createpage = kwargs.setdefault('create',False)
    if not createpage:
        reporter = get_object_or_404(Dashboard, slug=slug, user=None)
    return generic_dashboard(request,
        slug=slug,
        module_types=[('ureport', PollModuleForm, 'uReport Visualizations',),
                       ('static', StaticModuleForm, 'Static Content',),],
        base_template=base_template,
        title=None,**kwargs)

def message_feed(request):
    polls = retrieve_poll(request)
    poll = polls[0]
    return render_to_response(
        '/ureport/partials/viz/message_feed.html',
        {'poll':poll,'responses':_get_responses(poll)},
        context_instance=RequestContext(request))

@cache_control(no_cache=True, max_age=0)
def poll_summary(request):
    polls = Poll.objects.order_by('-start_date')
    return render_to_response(
        '/ureport/poll_summary.html',
        {'polls':polls,
         'poll':polls[0]},
        context_instance=RequestContext(request))

def get_all_contacts(request):
    from uganda_common.utils import ExcelResponse
    contacts=Contact.objects.all()
    export_data_list=[]
    for contact in contacts:
        if contact.name:
            export_data=SortedDict()
            export_data['name']=contact.name
            if contact.gender:
                export_data['sex']=contact.gender
            else:
                export_data['sex']='N/A'    
            if contact.birthdate:
                try:
                    contact.birthdate.tzinfo=None
                    export_data['age']=(datetime.datetime.now()-contact.birthdate).days/365
                except:
                    continue
            else:
                export_data['age']='N/A'
            if contact.reporting_location:
                export_data['district']=contact.reporting_location.name
            else:
                export_data['district']='N/A'
            if contact.village:
                export_data['village']=contact.village.name
            else:
                export_data['village']='N/A'
            if contact.groups.count()>0:
                export_data['group']=contact.groups.all()[0].name
            else:
                export_data['group']='N/A'

            export_data_list.append(export_data)

    response = ExcelResponse(export_data_list)
    return response

def bulk_upload_contacts(request):
    """
    bulk upload contacts from an excel file
    """
    if request.method == 'POST':
        contactsform = ExcelUploadForm(request.POST, request.FILES)
        if contactsform.is_valid():
            if contactsform.is_valid() and request.FILES.get('excel_file',None):
                fields=['telephone number','name', 'district', 'county', 'village', 'age', 'gender']
                message= handle_excel_file(request.FILES['excel_file'],contactsform.cleaned_data['assign_to_group'], fields)
            return render_to_response('ureport/bulk_contact_upload.html', 
                                      {'contactsform':contactsform,
                                       'message':message
                                       }, context_instance=RequestContext(request))

    contactsform = ExcelUploadForm()
    return render_to_response('ureport/bulk_contact_upload.html', 
                              {'contactsform':contactsform
                               }, context_instance=RequestContext(request))
    
def handle_excel_file(file,group, fields):
    if file:
        excel = file.read()
        workbook = open_workbook(file_contents=excel)
        worksheet = workbook.sheet_by_index(0)
        cols = parse_header_row(worksheet, fields)
        contacts = []
        duplicates = []
        invalid = []
        info = ''

        if not group:
            default_group = Group.objects.filter(name__icontains='ureporters')[0]
            group = default_group

        if worksheet.nrows > 1:
            validated_numbers = []
            for row in range(1,worksheet.nrows):
                numbers = parse_telephone(row, worksheet, cols)
                for raw_num in numbers.split('/'):
                    if raw_num[-2:] == '.0':
                        raw_num = raw_num[:-2]
                    if raw_num[:1] == '+':
                        raw_num = raw_num[1:]
                    if len(raw_num) >= 9:
                        validated_numbers.append(raw_num)
            duplicates = Connection.objects.filter(identity__in=validated_numbers).values_list('identity',flat=True)

            for row in range(1,worksheet.nrows):
                numbers = parse_telephone(row, worksheet, cols)
                if len(numbers) > 0:
                    contact = {}
                    contact['name']=parse_name(row,worksheet,cols)
                    district = parse_district(row, worksheet, cols) if 'district' in fields else None
                    village = parse_village(row, worksheet, cols) if 'village' in fields else None
                    birthdate = parse_birthdate(row, worksheet, cols) if 'age' in fields else None
                    gender = parse_gender(row, worksheet, cols) if 'gender' in fields else None
                    if district:
                        contact['reporting_location'] = find_closest_match(district, Area.objects.filter(kind__name='district'))
                    if village:
                        contact['village'] = find_closest_match(village, Area.objects)
                    if birthdate:
                        contact['birthdate'] = birthdate
                    if gender:
                        contact['gender'] = gender
                    if group:
                        contact['groups'] = group
    
                    for raw_num in numbers.split('/'):
                        if raw_num[-2:] == '.0':
                            raw_num = raw_num[:-2]
                        if raw_num[:1] == '+':
                            raw_num = raw_num[1:]
                        if len(raw_num) >= 9:
                            if raw_num not in duplicates:
                                number, backend = assign_backend(raw_num)
                                if number not in contacts and backend is not None:
                                    Connection.bulk.bulk_insert(send_pre_save=False,
                                                                identity=number,
                                                                backend=backend,
                                                                contact=contact)
                                    contacts.append(number)
                                elif backend is None:
                                    invalid.append(raw_num)
    
                        else:
                            invalid.append(raw_num)

            connections = Connection.bulk.bulk_insert_commit(send_post_save=False, autoclobber=True)
            contact_pks = connections.values_list('contact__pk',flat=True)
            
            if "authsites" in settings.INSTALLED_APPS:
                contact_queryset = Contact.allsites.filter(pk__in=contact_pks)
                from authsites.models import ContactSite
                ContactSite.add_all(contact_queryset)
                    
            if len(contacts)>0:
                info = 'Contacts with numbers... ' +' ,'.join(contacts) + " have been uploaded !\n\n"
            if len(duplicates)>0:
                info = info + 'The following numbers already exist in the system and thus have not been uploaded: ' +' ,'.join(duplicates)+ '\n\n'
            if len(invalid)>0:
                info = info + 'The following numbers may be invalid and thus have not been added to the system: '+' ,'.join(invalid)+ '\n\n'
        else:
            info = "You seem to have uploaded an empty excel file, please fill the excel Contacts Template with contacts and upload again..."
    else:
        info = "Invalid file"  
    return info
    
def parse_header_row(worksheet, fields):
#    fields=['telephone number','name', 'district', 'county', 'village', 'age', 'gender']
    field_cols={}
    for col in range(worksheet.ncols):
        value = str(worksheet.cell(0, col).value).strip()
        if value.lower() in fields:
            field_cols[value.lower()] = col
    return field_cols


def parse_telephone(row,worksheet,cols):
    try:
        number = str(worksheet.cell(row, cols['telephone number']).value)
    except KeyError:
        number = str(worksheet.cell(row, cols['telephone']).value)
    return number.replace('-','').strip().replace(' ','')

def parse_name(row,worksheet,cols):
    try:
        name = str(worksheet.cell(row, cols['company name']).value).strip()
    except KeyError:
        name = str(worksheet.cell(row, cols['name']).value).strip()
    if name.__len__() > 0:
#        name = str(worksheet.cell(row, cols['name']).value)
        return ' '.join([t.capitalize() for t in name.lower().split()])
    else:
        return 'Anonymous User'

def parse_district(row, worksheet, cols):
    return str(worksheet.cell(row, cols['district']).value)

def parse_village(row, worksheet, cols):
    return str(worksheet.cell(row, cols['village']).value)

def parse_birthdate(row, worksheet, cols):
    try:
        age = int(worksheet.cell(row, cols['age']).value)
        birthdate= '%d/%d/%d'%(datetime.datetime.now().day, datetime.datetime.now().month,datetime.datetime.now().year-age)
        return datetime.datetime.strptime(birthdate.strip(),'%d/%m/%Y')
    except ValueError:
        return None

def parse_gender(row, worksheet, cols):
    gender = str(worksheet.cell(row, cols['gender']).value)
    return gender.upper()[:1] if gender else None

def download_contacts_template(request, f):
    path = getattr(settings, 'DOWNLOADS_FOLDER', None)
    fh = open(path+f)
    data = File(fh).read()
    response = HttpResponse(data, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+f
    return response

def clickatell_wrapper(request):
    import pdb;pdb.set_trace()
    request.GET = request.GET.copy()
    request.GET.update({'backend':'clickatell','sender':request.GET['from'],'message':request.GET['text']})
    return receive(request)