#!/usr/bin/python
# -*- coding: utf-8 -*-

from ureport.models import IgnoredTags
import random
import types
from ureport.settings import drop_words, tag_cloud_size
from poll.models import Poll, Response
from django.db import connection
from django.conf import settings
from django.core.paginator import Paginator


TAG_CLASSES = ['tag14', 'tag13', 'tag12', 'tag11', 'tag10', 'tag9', 'tag8', 'tag7', 'tag6', 'tag5', 'tag4', 'tag3',
               'tag2', 'tag1']


def dictinvert(dict):
    inv = {}
    for k, v in dict.iteritems():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


def _get_tags(polls):
    word_count = {}
    if isinstance(polls, types.ListType):
        p_list = [poll.pk for poll in polls]
        poll_pks = str(Poll.objects.filter(pk__in=p_list).values_list('pk', flat=True))[1:-1]
    else:
        poll_pks = str(polls.values_list('pk', flat=True))[1:-1]
    sql = """  SELECT
           (regexp_matches(lower(word),E'[a-zA-Z]+'))[1] as wo,
           count(*) as c
        FROM
           (SELECT
              regexp_split_to_table("rapidsms_httprouter_message"."text",
              E'\\\\s+') as word
           from
              "rapidsms_httprouter_message"
           JOIN
              "poll_response"
                 ON "poll_response"."message_id"= "rapidsms_httprouter_message"."id"
           where
              poll_id in (%(polls)s)
              and has_errors='f')t
        WHERE
           NOT (word in (SELECT
              "ureport_ignoredtags"."name"
           FROM
              "ureport_ignoredtags"
           WHERE
              "ureport_ignoredtags"."poll_id" in (%(polls)s)))

        GROUP BY
           wo
        order by
           c DESC limit 200;   """ % {'polls': poll_pks}

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    rows_dict = dict(rows)
    bl = list(IgnoredTags.objects.filter(poll__in=polls).values_list("name", flat=True))
    for key in rows_dict.keys():
        if len(key) > 2 and not key in drop_words + bl:
            word_count[str(key)] = int(rows_dict[key])

    #gen inverted dictionary
    counts_dict = dictinvert(word_count)

    tags = generate_tag_cloud(word_count, counts_dict, TAG_CLASSES)

    # randomly shuffle tags

    random.shuffle(tags)
    return tags


def generate_tag_cloud(
        words,
        counts_dict,
        tag_classes
):
    """
        returns tag words with assosiated tag classes depending on their frequency
    @params:
             words: a dictionary of words and their associated counts
             counts_dict: a dictionary of counts and their associated words
             tag_classes: a list of tag classes sorted minumum to max
            """
    tags = []
    used_words_list = []
    divisor = tag_cloud_size / len(tag_classes) + 1
    if not counts_dict:
        return []
    c_keys = counts_dict.keys()
    c_keys.sort()
    c_keys.reverse()
    for count in c_keys:
        for word in counts_dict[count]:
            if not word in used_words_list:
                k = {}
                klass = tag_classes[len(tags) / divisor]

                #url reverse hates single quotes. turn to double quotes
                k['tag'] = "%s" % word
                k['class'] = klass
                tags.append(k)
                used_words_list.append(word)
                if len(used_words_list) == tag_cloud_size:
                    return tags

    return tags


def _get_responses(poll):
    bad_words = getattr(settings, 'BAD_WORDS', [])
    responses = Response.objects.filter(poll=poll)
    for helldamn in bad_words:
        responses = responses.exclude(message__text__icontains=' %s '
                                                               % helldamn).exclude(message__text__istartswith='%s '
                                                                                                              % helldamn)
    paginator = Paginator(responses, 8)
    responses = paginator.page(1).object_list
    return responses
