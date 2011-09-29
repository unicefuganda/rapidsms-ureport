#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from models import Flag, MessageFlag
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from rapidsms.contrib.handlers.handlers.base import BaseHandler

class CustomPatternHandler(BaseHandler):

    @classmethod
    def _pattern(cls):
        if hasattr(cls, "pattern_list"):
          
            return cls.pattern_list
            

    @classmethod
    def dispatch(cls, router, msg):

        pattern_list=cls._pattern()
        for reg in pattern_list:
            match= reg[0].search(msg.text)
            if match:
                MessageFlag.objects.create(message=msg,flag=reg[1])

        if match is None:
            return False
        #cls(router, msg).handle(*match.groups())
        return True
    
class FlagHandler(CustomPatternHandler):
    """
    Handle any message containing one of the keywords as from the flagged messages
    table
    """
    flags=Flag.objects.all()
    pattern_list=[[re.compile(flag.rule, re.IGNORECASE),flag] for flag in flags if flag.rule ]
    def handle(self, text):
        pass
