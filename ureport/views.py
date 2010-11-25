from django.shortcuts import  render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django import forms
from django.contrib.auth.models import Group
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.conf import settings

from ureport.settings import *
from ureport.models import IgnoredTags
from poll.models import *

from rapidsms.models import Contact
from rapidsms_httprouter.router import get_router, start_sending_mass_messages, stop_sending_mass_messages
from rapidsms.messages.outgoing import OutgoingMessage

from authsites.models import ContactSite,GroupSite

import re
import bisect
import textwrap

TAG_CLASSES=['tag1','tag2','tag3','tag4','tag5','tag6','tag7']

def index(request):
    return render_to_response("ureport/index.html", {}, RequestContext(request)) 


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
                if (len(used_words_list)==Tag_Cloud_Words):
                    return tags

    return tags


def add_drop_word(request):
    tag_name=request.GET.get('tag',None)
    poll_pk=int(request.GET.get('poll',1))
    IgnoredTags.objects.create(name=tag_name,poll=Poll.objects.get(pk=poll_pk))
    return HttpResponse(simplejson.dumps("success"))

def delete_drop_word(request):
    tag_name=request.GET.get('tag',None)
    tags=IgnoredTags.objects.filter(name=tag_name)
    print tags
    for tag in tags:
        tag.delete()
    return HttpResponse(simplejson.dumps("success"))

def show_ignored_tags(request):
    tags=IgnoredTags.objects.all()
    return render_to_response("ureport/partials/ignored_tags.html", {'tags':tags},context_instance=RequestContext(request))


def tag_cloud(request):
    """
        generates a tag cloud
    """
    
    pks=request.GET.get('pks', '').split('+')
    pks=[eval(x) for x in list(str(pks[0]).rsplit())]
    responses=Response.objects.filter(poll__pk__in=pks)
    words=''
    word_count={}
    counts_dict={}
    used_words_list=[]
    max_count=0
    reg_words= re.compile(r'\W+')
    dropwords=IgnoredTags.objects.filter(poll__id__in=pks).values_list('name',flat=True)
    for response in responses:
        if  response.eav.poll_text_value:
            for word in reg_words.split(response.eav.poll_text_value):
                if word not in dropwords and len(word) >2:
                    word_count.setdefault(word,0)
                    word_count[word]+=1
                    if  counts_dict.get(word_count[word],None):
                        counts_dict[word_count[word]].append(word)
                    else:
                        counts_dict[word_count[word]]=[]
                        counts_dict[word_count[word]].append(word)

                    if word_count[word]>max_count:
                        max_count=word_count[word]
        else:
            continue

    tags=generate_tag_cloud(word_count,counts_dict,TAG_CLASSES,max_count)

    return render_to_response("ureport/partials/tag_cloud.html", {'tags':tags},
                              context_instance=RequestContext(request))


def polls(request,template,type=None):
    """
        view for freeform polls
    """
    
    if type:
        polls = Poll.objects.filter(type=type)
    else:
        polls=Poll.objects.all()
    return render_to_response(template, {'polls':polls}, context_instance=RequestContext(request))


class MessageForm(forms.Form): # pragma: no cover
    contacts = forms.ModelMultipleChoiceField(required=False,queryset=Contact.objects.filter(pk__in=ContactSite.objects.filter(site=Site.objects.get_current()).values_list('contact', flat=True)))
    groups = forms.ModelMultipleChoiceField(required=False,queryset=Group.objects.filter(pk__in=GroupSite.objects.filter(site=Site.objects.get_current()).values_list('group', flat=True)))
    text = forms.CharField(max_length=160, required=True, widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}))


def messaging(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            router = get_router()
            
            contacts = form.cleaned_data['contacts']
            groups = form.cleaned_data['groups']
            if hasattr(Contact, 'groups'):
                connections = Connection.objects.filter(Q(contact__in=contacts) | Q(contact__groups__in=groups)).distinct()
            else:
                connections = Connection.objects.filter(contact__in=contact).distinct()
            recipients = 0
            start_sending_mass_messages()
            for conn in connections:
                text = form.cleaned_data['text'].replace('%', '%%')
                outgoing = OutgoingMessage(conn, text)
                router.handle_outgoing(outgoing)
                recipients = recipients + 1
            stop_sending_mass_messages()
            return render_to_response("ureport/messaging.html", {'recipients':recipients, 'form':MessageForm()}, context_instance=RequestContext(request))
        else:
            return render_to_response("ureport/messaging.html", {'form':form}, context_instance=RequestContext(request))
    else:
        form = MessageForm()
        return render_to_response("ureport/messaging.html", {'form':MessageForm()}, context_instance=RequestContext(request))


def pie_graph(request):
    """
        view for pie-chart

    """
    all_polls=Poll.objects.all()
    if request.GET.get('pks', None):
        pks=request.GET.get('pks', '').split('+')
        pks=[eval(x) for x in list(str(pks[0]).rsplit())]
        responses=Response.objects.filter(poll__pk__in=pks)

        poll_names=['Qn:'+'<br>'.join(textwrap.wrap(poll.question.rsplit('?')[0]))+'?<br>' for poll in Poll.objects.filter(pk__in=pks)]

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


def histogram(request):
    """
         view for numeric polls
    """

    all_polls=Poll.objects.filter(type=u'n')
    if request.GET.get('pks', None):
        items=6
        pks=request.GET.get('pks', '').split('+')
        pks=[eval(x) for x in list(str(pks[0]).rsplit())]
        responses=Response.objects.filter(poll__pk__in=pks,poll__type=u'n')
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
    colors=['#4572A7', '#AA4643', '#89A54E', '#80699B', '#3D96AE', '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92']
    polls=Poll.objects.all()
    map_key = settings.MAP_KEY
    Map_urls = mark_safe(simplejson.dumps(MAP_URLS))
    map_types = mark_safe(simplejson.dumps(MAP_TYPES))
    (minLon, maxLon, minLat, maxLat) = (mark_safe(min_lat),
            mark_safe(max_lat), mark_safe(min_lon), mark_safe(max_lon))
    if request.GET.get('pks', None):
        pks=request.GET.get('pks', '').split('+')
        pks=[eval(x) for x in list(str(pks[0]).rsplit())]
        responses=Response.objects.filter(poll__pk__in=pks)
        layer_values={}
        all_categories=set()
        for response in responses:
            if response.message:
                loc=response.message.connection.contact.reporting_location
                if loc:
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

        layer_values['colors']={}
        #set colors for category types
        i=0
        layer_values['colors']["uncategorized"]="#ff0000"
        for cat in Category.objects.all():
            try:
                layer_values['colors'][cat.name]=colors[i]
                i+=1
            except IndexError:
                layer_values['colors'][cat.name]='#000000'

        return HttpResponse(mark_safe(simplejson.dumps(layer_values)) )
    # FIXME don't use locals
    return render_to_response("ureport/map.html", locals(), context_instance=RequestContext(request))


def poll_dashboard(request):
    polls=Poll.objects.all()
    colors=['#4572A7', '#AA4643', '#89A54E', '#80699B', '#3D96AE', '#DB843D', '#92A8CD', '#A47D7C', '#B5CA92']
    polls=Poll.objects.all()
    map_key = settings.MAP_KEY
    Map_urls = mark_safe(simplejson.dumps(MAP_URLS))
    map_types = mark_safe(simplejson.dumps(MAP_TYPES))
    (minLon, maxLon, minLat, maxLat) = (mark_safe(min_lat),
            mark_safe(max_lat), mark_safe(min_lon), mark_safe(max_lon))
    
    # FIXME don't use locals
    return render_to_response("ureport/dashboard.html", locals(), context_instance=RequestContext(request))

