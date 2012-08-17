# -*- coding: utf-8 -*-
from django.db import models

class ContactExport(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    language = models.CharField(max_length=6)
    autoreg_join_date = models.DateField()
    quit_date = models.DateTimeField()
    district = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1)
    facility = models.CharField(max_length=50)
    village = models.CharField(max_length=100)
    group = models.CharField(max_length=80)
    source = models.TextField()
    responses = models.IntegerField()
    questions = models.IntegerField()
    incoming = models.IntegerField()
    class Meta:
        db_table="contacts_export"
        app_label = 'ureport'

class AlertsExport(models.Model):
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    message = models.TextField()
    direction = models.CharField(max_length=1)
    date = models.DateTimeField()
    mobile = models.CharField(max_length=100)
    rating = models.CharField(max_length=500)
    replied = models.CharField(max_length=50)
    forwarded = models.CharField(max_length=50)
    class Meta:
        db_table="alerts_export"
        app_label = 'ureport'
