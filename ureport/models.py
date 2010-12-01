from django.db import models
from poll.models import Poll
from rapidsms.models import Contact
from django.contrib.auth.models import User

class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name=models.CharField(max_length=20)

    def __unicode__(self):
        return '%s'%self.name

class MassText(models.Model):
    contacts = models.ManyToManyField(Contact, related_name='masstexts')
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True,null=True)
    text = models.CharField(max_length=160)


