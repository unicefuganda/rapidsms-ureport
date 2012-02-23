from django.db import models

from rapidsms.models import ContactBase

class ActivatedcContact(models.Model):
    """
    This extension for Contacts allows developers to tie a Contact to
    the Location object they're reporting from.
    """
    health_facility = models.CharField(null=True,blank=True,max_length=50)

    class Meta:
        abstract = True