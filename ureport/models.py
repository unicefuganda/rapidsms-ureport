from django.db import models
from poll.models import Poll, LocationResponseForm, STARTSWITH_PATTERN_TEMPLATE
from rapidsms.models import Contact
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.conf import settings
from simple_locations.models import Area, AreaType
from eav.models import Attribute
from django.core.exceptions import ValidationError

import re
import difflib

class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name=models.CharField(max_length=20)

    def __unicode__(self):
        return '%s'%self.name

class MassText(models.Model):
    sites = models.ManyToManyField(Site)
    contacts = models.ManyToManyField(Contact, related_name='masstexts')
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True,null=True)
    text = models.TextField()
    objects = (CurrentSiteManager('sites') if settings.SITE_ID else models.Manager())
    
    class Meta:
        permissions = (
            ("can_message", "Can send messages, create polls, etc"),
        )

def parse_district_value(value):
    location_template = STARTSWITH_PATTERN_TEMPLATE % '[a-zA-Z]*'
    regex = re.compile(location_template)
    try:
        if regex.search(value):
            spn = regex.search(value).span()
            location_str = value[spn[0]:spn[1]]
            area = None
            area_names = Area.objects.filter(kind__name='district').values_list('name', flat=True)
            area_names_lower = [ai.lower() for ai in area_names]
            area_names_matches = difflib.get_close_matches(location_str.lower(), area_names_lower)
            if area_names_matches:
                area = Area.objects.get(name__iexact=area_names_matches[0], kind__name='district')
                return area
    except:
        pass
    raise ValidationError("We didn't recognize your district.  Please carefully type the name of your district and re-send.")

Poll.register_poll_type('district', 'District Response', parse_district_value, db_type=Attribute.TYPE_OBJECT,\
                        view_template='polls/response_location_view.html',
                        edit_template='polls/response_location_edit.html',
                        report_columns=(('Text','text'),('Location','location'),('Categories','categories')),
                        edit_form=LocationResponseForm)
