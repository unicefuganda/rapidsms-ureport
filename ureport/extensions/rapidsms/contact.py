from django.db import models

from rapidsms.models import ContactBase
from rapidsms.contrib.locations.models import Location

class ActivatedcContact(models.Model):
    """
    This extension for Contacts allows developers to tie a Contact to
    the Location object they're reporting from.
    """
    health_facility = models.CharField(null=True,blank=True,max_length=50)
    is_caregiver = models.BooleanField(default=False)
    occupation = models.CharField(null=True,blank=True,max_length=50)
    subcounty = models.ForeignKey('locations.Location', blank=True, null=True, related_name='subcounties')

    class Meta:
        abstract = True