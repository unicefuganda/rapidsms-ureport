from django.shortcuts import  render_to_response
from django.template import RequestContext

from ureport.settings import drop_words,Tag_Cloud_Words
from poll.models import *

import re

tag_classes=['tag1','tag2','tag3','tag4','tag5','tag6','tag7']
def ureport(request):
    return render_to_response("ureport/index.html", context_instance=RequestContext(request))

def generate_tag_cloud(words,counts_dict,tag_classes,max_count):
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
    pks=list(set(request.GET.get('pks', '').split('+')))
    responses=Response.objects.filter(poll__pk__in=pks)
    words=''
    word_count={}
    counts_dict={}
    used_words_list=[]
    max_count=0
    reg_words= re.compile(r'\W+')
    for response in responses:
        for word in reg_words.split(response.message.text):
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




    tags=generate_tag_cloud(word_count,counts_dict,tag_classes,max_count)


    return render_to_response("ureport/tag_cloud.html", {'tags':tags},
                              context_instance=RequestContext(request))


def freeform_polls(request):
    free_form_polls = Poll.objects.filter(type=u't')
    return render_to_response("ureport/polls.html", {'polls':free_form_polls}, context_instance=RequestContext(request))