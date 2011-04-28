from django.shortcuts import  render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.db.models import Q
from django import forms
from django.contrib.auth.models import Group
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required

from ureport.settings import colors, drop_words, tag_cloud_size
from ureport.models import IgnoredTags
from poll.models import *

from rapidsms.models import Contact
from rapidsms_httprouter.router import get_router, start_sending_mass_messages, stop_sending_mass_messages
from djtables import Column, Table
from djtables.column import DateColumn
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms_httprouter.models import Message, DIRECTION_CHOICES, STATUS_CHOICES

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from generic.views import generic

from .models import MassText
from .forms import EditReporterForm, ReplyForm
from .utils import retrieve_poll

import re
import bisect
import textwrap
import random

TAG_CLASSES=['tag1','tag2','tag3','tag4','tag5','tag6','tag7']

def index(request):
    return render_to_response("ureport/index.html", {}, RequestContext(request)) 

@login_required
def tag_view(request):
    return render_to_response("ureport/tag_cloud.html", context_instance=RequestContext(request))


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
    divisor = (max_count / len(tag_classes)) + 1
    for i in range(max_count,0,-1):
        for word in counts_dict[i]:
            if not word in used_words_list:
                k={}
                klass=tag_classes[i/divisor]
                k['tag']=word
                k['class']=klass
                tags.append(k)
                used_words_list.append(word)
                if (len(used_words_list)==tag_cloud_size):
                    return tags

    return tags

@login_required
def add_drop_word(request):
    tag_name=request.GET.get('tag',None)
    poll_pk=int(request.GET.get('poll',1))
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
def show_ignored_tags(request):
    tags=IgnoredTags.objects.all()
    return render_to_response("ureport/partials/ignored_tags.html", {'tags':tags},context_instance=RequestContext(request))

def tag_cloud(request):
    """
        generates a tag cloud
    """
    polls = retrieve_poll(request)
    responses=Response.objects.filter(poll__in=polls)
    words=''
    word_count={}
    counts_dict={}
    used_words_list=[]
    max_count=0
    reg_words = re.compile('[^a-zA-Z]')
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

    return render_to_response("ureport/partials/tag_cloud.html", {'tags':tags,'poll_qn':poll_qn[0]},
                              context_instance=RequestContext(request))

@login_required
def polls(request,template,type=None):
    """
        view for freeform polls
    """
    
    if type:
        polls = Poll.objects.filter(type=type)
    else:
        polls=Poll.objects.all()
    return render_to_response(template, {'polls':polls}, context_instance=RequestContext(request))

def pie_graph(request):
    """
        view for pie-chart

    """

    all_polls=Poll.objects.all()
    if request.GET.get('pks', None):
        polls = retrieve_poll(request)
        responses=Response.objects.filter(poll__in=polls)

        poll_names=['Qn:'+'<br>'.join(textwrap.wrap(poll.question.rsplit('?')[0]))+'?<br>' for poll in polls]

        total_responses=responses.count()
        category_count={}
        plottable_data={}
        plottable_data['data']=[]
        plottable_data['poll_names']=''.join(poll_names).encode("iso-8859-15", "replace")
        uncategorized=0
        for response in responses:
            if response.categories.count() >0:
                categories=  [r.category.name for r in response.categories.all()]
                if len(categories) > 1:
                    key=' and '.join(categories)
                else:
                    key=  str(categories[0])
                category_count.setdefault(key,0)
                category_count[key]+=1
            else:
                uncategorized+=1
        category_count['uncategorized']=uncategorized

        for k in category_count.keys():
            plottable_data['data'].append([k,(category_count[k]*100)/total_responses])

        return HttpResponse(mark_safe(simplejson.dumps(plottable_data)) )

    return render_to_response("ureport/pie_graph.html", {'polls':all_polls}, context_instance=RequestContext(request))

def piegraph_module(request):
    polls = retrieve_poll(request)
    poll = polls[0]
    return render_to_response("ureport/partials/piechart_module.html", {"poll":poll}, context_instance=RequestContext(request))

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

def map(request):
    polls=Poll.objects.all()
    if request.GET.get('pks', None):
        polls = retrieve_poll(request)
        responses=Response.objects.filter(poll__in=polls)
        layer_values={}
        layer_values['colors']={}
        for response in responses:
            if response.message:
                loc=response.message.connection.contact.reporting_location
                if loc:
                    try:
                        layer_values.setdefault(loc.name,{'lat':float(loc.location.latitude),'lon':float(loc.location.longitude)})
                        if response.categories.count()>0:
                            categories=  [r.category.name for r in response.categories.all()]
                            if len(categories) > 1:
                                key=' and '.join(categories)
                            else:
                                key=  str(categories[0])
                            layer_values[loc.name].setdefault('data',{})
                            layer_values[loc.name]['data'].setdefault(key,0)
                            layer_values[loc.name]['data'][key]+=1
                        else:
                            layer_values[loc.name].setdefault('data',{})
                            layer_values[loc.name]['data'].setdefault('uncategorized',0)
                            layer_values[loc.name]['data']['uncategorized']+=1
                            if layer_values[loc.name]['data']['uncategorized'] >0:
                                layer_values['colors']["uncategorized"]="#ff0000"
                    except:
                        continue
        #set colors for category types
        i=0
        #poll question
        poll_qn=['Qn:'+'<br>'.join(textwrap.wrap(poll.question.rsplit('?')[0]))+'?<br>' for poll in polls]
        layer_values['qn']=poll_qn
        for cat in Category.objects.filter(poll__in=polls):
            try:
                layer_values['colors'][cat.name]=colors[i]
                i+=1
            except IndexError:
                layer_values['colors'][cat.name]='#000000'

        return HttpResponse(mark_safe(simplejson.dumps(layer_values)))

    return render_to_response("ureport/map.html", {'polls':polls}, context_instance=RequestContext(request))

def mapmodule(request):
    polls = retrieve_poll(request)
    poll = polls[0]
    return render_to_response("ureport/partials/map_module.html", {'poll':poll}, context_instance=RequestContext(request)) 

@login_required
def view_message_history(request, connection_id):
    """
        This view lists all (sms message) correspondence between 
        RapidSMS and a User 
        
    """
    direction_choices   = DIRECTION_CHOICES
    status_choices      = STATUS_CHOICES
    reply_form = ReplyForm()
    try:
        connection          = get_object_or_404(Connection, pk=connection_id)

        if connection.contact:
            try:
                messages        = Message.objects.filter(connection__contact=connection.contact).order_by('-date')
                latest_message  = Message.objects.filter(connection__contact=connection.contact).filter(direction="I").latest('date')
                total_incoming  = Message.objects.filter(connection__contact=connection.contact).filter(direction="I").count()
                total_outgoing  = Message.objects.filter(connection__contact=connection.contact).filter(direction="O").count()
            except Message.DoesNotExist:
                messages = []
                latest_message = []
                total_incoming = 0
                total_outgoing = 0
        else:
            try:
                messages = Message.objects.filter(connection=connection).order_by('-date')
                latest_message  = Message.objects.filter(connection=connection).filter(direction="I").latest('date')
                total_incoming  = Message.objects.filter(connection=connection).filter(direction="I").count()
                total_outgoing  = Message.objects.filter(connection=connection).filter(direction="O").count()
            except Message.DoesNotExist:
                messages = []
                latest_message = []
                total_incoming = 0
                total_outgoing = 0

        #reply_form = str(reply_form).replace("\n","")
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
    except Http404:
        connection = None
        messages = []
        latest_message = []
        total_incoming = 0
        total_outgoing = 0
    return render_to_response("ureport/message_history.html", {
                        "messages": messages,
                        "stats_latest_message": latest_message,
                        "stats_total_incoming": total_incoming,
                        "stats_total_outgoing": total_outgoing, 
                        "connection": connection, 
                        "direction_choices": direction_choices, 
                        "status_choices": status_choices,
                        "replyForm": reply_form
                        }
    , context_instance=RequestContext(request))

def show_timeseries(request):
    polls = retrieve_poll(request)
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

    return render_to_response("ureport/partials/timeseries.html",{'counts':mark_safe(message_count_list),'start':start_date,'end':end_date,'poll':mark_safe(poll)},context_instance=RequestContext(request))


@login_required
def deleteReporter(request, reporter_pk):
    reporter = get_object_or_404(Contact, pk=reporter_pk)
    if request.method == 'POST':
        reporter.delete()

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
            return render_to_response('ureport/partials/edit_reporter.html'
                    , {'reporter_form': reporter_form, 'reporter'
                    : reporter},
                    context_instance=RequestContext(request))
        return render_to_response('/ureport/partials/contacts_row.html',
                                  {'object':Contact.objects.get(pk=reporter_pk)},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('ureport/partials/edit_reporter.html',
                                  {'reporter_form': reporter_form,
                                  'reporter': reporter},
                                  context_instance=RequestContext(request))

@login_required
def view_responses(req, poll_id):
    poll = get_object_or_404(Poll,pk=poll_id)

    responses = poll.responses.all().order_by('-date')
    typedef = Poll.TYPE_CHOICES[poll.type]
    columns = [('Sender', False, 'sender', None)]
    for column, style_class in typedef['report_columns']:
        columns.append((column, False, style_class, None))

    return generic(req,
        model=Response,
        queryset=responses,
        objects_per_page=25,
        selectable=False,
        partial_base='ureport/partials/poll_partial_base.html',
        row_base=typedef['view_template'],
        columns=columns,
        partial_row='ureport/partials/response_row.html'
    )
    
def best_visualization(req):
    view_dict = {
        'c':mapmodule,
        'n':histogram,
        't':tag_cloud,
    }
    polls = retrieve_poll(req)
    poll = polls[0]
    poll_type = 'c' if poll.categories.count() else poll.type
    poll_type = poll_type if poll_type in view_dict else 't'
    return view_dict[poll_type](req)

def message_feed(request):
    polls = retrieve_poll(request)
    poll = polls[0]
    bad_words = getattr(settings, 'BAD_WORDS', [])
    responses = Response.objects.filter(poll=poll)
    for helldamn in bad_words:
        responses = responses.exclude(message__text__icontains=(" %s " % helldamn)).exclude(message__text__istartswith=("%s " % helldamn))
    paginator = Paginator(responses, 8)
    responses = paginator.page(1).object_list
    return render_to_response(
        '/ureport/partials/message_feed.html',
        {'poll':poll,'responses':responses},
        context_instance=RequestContext(request))