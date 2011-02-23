from django.db import models
from poll.models import Poll
from rapidsms.models import Contact
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

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


