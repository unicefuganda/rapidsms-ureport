from django.db import models

from rapidsms.models import ContactBase

from simple_locations.models import Area

class DemographicContact(models.Model):
    """
    This extension for Contacts allows developers to tie a Contact to
    the Area object they're reporting from.  This extension
    depends on the simple_locations app.
    """
    birthdate = models.DateTimeField(null=True)
    gender = models.CharField(
            max_length=1,
            choices=(('M', 'Male'),('F', 'Female')), null=True)
    village = models.ForeignKey(Area, blank=True, null=True, related_name='villagers')
    

    class Meta:
        abstract = True