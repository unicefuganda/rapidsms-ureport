from django.shortcuts import  render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django import forms
from django.contrib.auth.models import Group
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.http import HttpResponse

from ureport.settings import drop_words,Tag_Cloud_Words
from poll.models import *

from rapidsms.models import Contact
from rapidsms_httprouter.router import get_router
from rapidsms.messages.outgoing import OutgoingMessage
from authsites.models import ContactSite,GroupSite
import re
import bisect

tag_classes=['tag1','tag2','tag3','tag4','tag5','tag6','tag7']
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
    for response in responses:
        if response.eav.poll_text_value:
            for word in reg_words.split(response.eav.poll_text_value):
                if word not in drop_words and len(word) >2:
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




    tags=generate_tag_cloud(word_count,counts_dict,tag_classes,max_count)


    return render_to_response("ureport/partials/tag_cloud.html", {'tags':tags},
                              context_instance=RequestContext(request))


def freeform_polls(request):

    """
        view for freeform polls
    """
    free_form_polls = Poll.objects.filter(type=u't')
    return render_to_response("ureport/partials/freeform_polls.html", {'polls':free_form_polls}, context_instance=RequestContext(request))


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
            for conn in connections:
                text = form.cleaned_data['text'].replace('%', '%%')
                outgoing = OutgoingMessage(conn, text)
                router.handle_outgoing(outgoing)
                recipients = recipients + 1
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

        poll_names=['Qn:'+poll.question+'<br>' for poll in Poll.objects.filter(pk__in=pks)]

        total_responses=responses.count()
        category_count={}
        plottable_data={}
        plottable_data['data']=[]
        plottable_data['poll_names']=str(''.join(poll_names))
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
        responses=Response.objects.filter(poll__pk__in=pks)
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
        plottable_data={}
        plottable_data['data']=data
        plottable_data['title']  =poll_qns
        plottable_data['categories'] =ranges_list
        plottable_data['mean'] =sum(vals_list)/len(vals_list)
        plottable_data['median']=vals_list[len(vals_list)/2]
        return HttpResponse(mark_safe(simplejson.dumps(plottable_data)) )


    return render_to_response("ureport/histogram.html", {'polls':all_polls}, context_instance=RequestContext(request))
