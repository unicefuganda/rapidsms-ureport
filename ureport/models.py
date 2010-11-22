from django.db import models
from poll.models import Poll


class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name=models.CharField(max_length=20)

    def __unicode__(self):
        return '%s'%self.name