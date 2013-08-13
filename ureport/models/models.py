# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.db.transaction import commit_on_success, commit_manually
from openpyxl import reader
from poll.models import Poll
from rapidsms.models import Contact, Connection
from django.contrib.auth.models import User, Group
from rapidsms.contrib.locations.models import Location
from script.models import ScriptSession
from rapidsms_httprouter.models import Message
from unregister.models import Blacklist
from django.db.models.signals import post_save
from uganda_common.utils import assign_backend
from contact.models import Flag
from ussd.models import ussd_complete
import datetime
import re
from script.signals import script_progress_was_completed


class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        app_label = 'ureport'


class QuoteBox(models.Model):
    question = models.TextField()
    quote = models.TextField()
    quoted = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'creation_date'
        app_label = 'ureport'


class TopResponses(models.Model):
    poll = models.ForeignKey(Poll, related_name="top_responses")
    quote = models.TextField()
    quoted = models.TextField()

    class Meta:
        app_label = 'ureport'


class EquatelLocation(models.Model):
    serial = models.CharField(max_length=50)
    segment = models.CharField(max_length=50, null=True)
    location = models.ForeignKey(Location)
    name = models.CharField(max_length=50, null=True)

    class Meta:
        app_label = 'ureport'


class Permit(models.Model):
    user = models.ForeignKey(User)
    allowed = models.CharField(max_length=200)
    date = models.DateField(auto_now=True)

    def get_patterns(self):
        pats = []
        ropes = self.allowed.split(",")
        for rop in ropes:
            pattern = re.compile(rop + r"(.*)")
            pats.append(pattern)
        return pats

    def __unicode__(self):
        return self.user.username

    class Meta:
        app_label = 'ureport'


class Ureporter(Contact):
    from_cache = False

    def age(self):
        if self.birthdate:
            return (datetime.datetime.now() - self.birthdate).days / 365
        else:
            return ""

    def is_active(self):
        return not Blacklist.objects.filter(connection=self.default_connection)

    def join_date(self):
        ss = ScriptSession.objects.filter(connection__contact=self)
        if ss:
            return ScriptSession.objects.filter(connection__contact=self)[0].start_time.date()
        else:
            messages = Message.objects.filter(connection=self.default_connection).order_by('date')
            if messages:
                return messages[0].date
            else:
                return None

    def quit_date(self):
        quit_msg = Message.objects.filter(connection__contact=self, application="unregister")
        if quit_msg:
            return quit_msg.latest('date').date

    def messages_count(self):
        return Message.objects.filter(connection__contact=self, direction="I").count()

    class Meta:
        permissions = [
            ("view_numbers", "can view private info"),
            ("restricted_access", "can view only particular pages"),
            ("can_filter", "can view filters"),
            ("can_action", "can view actions"),
            ("view_number", "can view numbers"),
            ("can_export", "can view exports"),
            ("can_forward", "can forward messages"),

        ]

        proxy = True
        app_label = 'ureport'


class MessageAttribute(models.Model):
    '''
    The 'MessageAttribute' model represents a class of feature found
    across a set of messages. It does not store any data values
    related to the attribute, but only describes what kind of a
    message feature we are trying to capture.

    Possible attributes include things like number of replies,severity,department    etc
    '''
    name = models.CharField(max_length=300, db_index=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label = 'ureport'


class MessageDetail(models.Model):
    '''
    The 'MessageDetail' model represents information unique to a
    specific message. This is a generic design that can be used to
    extend the information contained in the 'Message' model with
    specific, extra details.
    '''

    message = models.ForeignKey(Message, related_name='details')
    attribute = models.ForeignKey('MessageAttribute')
    value = models.CharField(max_length=500)
    description = models.TextField(null=True)

    def __unicode__(self):
        return u'%s: %s' % (self.message, self.attribute)

    class Meta:
        app_label = 'ureport'


class Settings(models.Model):
    """
    configurable  sitewide settings. Its better to store in db table

    """
    attribute = models.CharField(max_length=50, null=False)
    value = models.CharField(default='', max_length=50, null=True)
    description = models.TextField(null=True)
    user = models.ForeignKey(User, null=True, blank=True)


    class Meta:
        app_label = 'ureport'


class AutoregGroupRules(models.Model):
    contains_all_of = 1
    contains_one_of = 2
    group = models.ForeignKey(Group, related_name="rules")
    rule = models.IntegerField(max_length=10,
                               choices=((contains_all_of, "contains_all_of"), (contains_one_of, "contains_one_of"),),
                               null=True, blank=True)
    values = models.TextField(default=None, null=True)
    closed = models.NullBooleanField(default=False)
    rule_regex = models.CharField(max_length=700, null=True)

    def get_regex(self):
        words = self.values.split(",")

        if self.rule == 1:
            all_template = r"(?=.*\b%s\b)"
            w_regex = r""
            for word in words:
                w_regex = w_regex + all_template % re.escape(word)
            return w_regex

        elif self.rule == 2:
            one_template = r"(\b%s\b)"
            w_regex = r""
            for word in words:
                if len(w_regex):
                    w_regex = w_regex + r"|" + one_template % re.escape(word)
                else:
                    w_regex = w_regex + one_template % re.escape(word)

            return w_regex

    def save(self, *args, **kwargs):
        if self.values:
            self.rule_regex = self.get_regex()
        super(AutoregGroupRules, self).save()


    class Meta:
        app_label = 'ureport'


from .litseners import autoreg, check_conn, update_latest_poll, ussd_poll, add_to_poll

script_progress_was_completed.connect(autoreg, weak=False)
post_save.connect(check_conn, sender=Connection, weak=False)
post_save.connect(update_latest_poll, sender=Poll, weak=False)
ussd_complete.connect(ussd_poll, weak=False)
#post_save.connect(add_to_poll, sender=Blacklist, weak=False)


class UPoll(Poll):
    def _get_set_attr(self):
        values = self.pollattributevalue_set.all()
        key_value = {}
        for value in values:
            try:
                key_value[value.get_key()] = value.get_value()
            except PollAttribute.DoesNotExist:
                pass
        return key_value

    def __init__(self, *args, **kwargs):
        super(UPoll, self).__init__(*args, **kwargs)
        #Attach PollAttribute to object ie, poll.randomkey = 'some value'
        for attr, value in self._get_set_attr().items():
            setattr(self, attr.key, value)
        #Attach Attribute default if no attribute set for specific poll
        for attr in PollAttribute.objects.all():
            if getattr(self, attr.key, None) is None:
                setattr(self, attr.key, attr.get_default())
                self.set_attr(attr.key, attr.get_default())


    @commit_manually
    def set_attr(self, attr, value):
        # import pdb;pdb.set_trace()
        print value, attr
        attr = PollAttribute.objects.get(key=attr)
        try:
            _value = attr.values.get(poll=self)
            _value.value = value
            _value.save()
            transaction.commit()
        except PollAttributeValue.DoesNotExist:
            _value = PollAttributeValue.objects.create(poll=self, value=value)
            attr.values.add(_value)
            attr.save()
            transaction.commit()

    def save(self, force_insert=False, force_update=False, using=None):

        for key in self._get_set_attr().keys():
            self.set_attr(key.key, getattr(self, key.key))
        super(UPoll, self).save()

    class Meta:
        proxy = True
        app_label = 'ureport'


class PollAttributeValueManager(models.Manager):
    def update(self, *args, **kwargs):
        raise NotImplementedError("Unfortunately you cannot call update() on this model yet. Sorry")


class PollAttributeValue(models.Model):
    value = models.CharField(max_length=200)
    poll = models.ForeignKey(Poll)
    objects = PollAttributeValueManager()

    def get_key(self):
        try:
            return self.pollattribute_set.all()[0]
        except IndexError:
            raise PollAttribute.DoesNotExist("%s value does not have a key attached to it" % self.value)

    def __unicode__(self):
        return self.value

    def get_value(self):
        key = self.get_key()
        return key.make_native(self.value)

    def save(self, force_insert=False, force_update=False, using=None):
        self.value = str(self.value).lower()
        super(PollAttributeValue, self).save()

    class Meta:
        app_label = 'ureport'


class PollAttribute(models.Model):
    """
    This is for any extra attributes that we would want on polls that rapidsms_polls does not have.

    """
    KEY_TYPES = (('bool', 'bool'), ('char', 'char'), ('int', 'int'), ('obj', 'obj'))
    key = models.CharField(max_length=100, unique=True)
    key_type = models.CharField(max_length=100, choices=KEY_TYPES, default='char')
    values = models.ManyToManyField(PollAttributeValue)
    default = models.CharField(max_length=100, null=True, default=None)


    class Meta:
        app_label = 'ureport'


    def __unicode__(self):
        return self.key


    def get_default(self):
        return self.make_native(self.default)

    def save(self, force_insert=False, force_update=False, using=None):
        self.default = str(self.default).lower()
        self.key = self.key.replace(" ", "_")
        super(PollAttribute, self).save()

    def make_native(self, default):
        if self.key_type == 'bool':
            return True if default.lower() == 'true' else False
        elif self.key_type == 'int':
            return int(default)
        else:
            return default


class SentToMtrac(models.Model):
    message = models.OneToOneField(Message)
    sent_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ureport'


class UploadContactException(Exception):
    pass


class UploadContacts(models.Model):
    excel_file = models.FileField(upload_to="excel_contacts")
    user = models.ForeignKey(User)
    unprocessed = models.TextField(blank=True)
    processed_on = models.DateTimeField(null=True)

    class Meta:
        app_label = "ureport"

    def get_unprocessed(self):
        return self.unprocessed

    def process(self):
        excel = reader.excel.load_workbook(self.excel_file.path)
        rows = []
        for sheet in excel.worksheets:
            for row in sheet.rows:
                r = []
                for cell in row:
                    r.append(cell.value)
                rows.append(tuple(r))
        with_error = []
        for row in rows:
            try:
                phone, group, name, language, gender, age, occupation, district, village_name, subcounty, health_facility = row
                district = self._get_district(str(district))
                phone = self._clean_phone(str(phone))
                birth_date = self._birth_date(str(age))
                gender = self._get_gender(str(gender))
                group = self._get_group(group)
                language = language if language else 'en'

                connection, created = Connection.objects.get_or_create(identity=phone, backend=assign_backend(phone)[1])
                if connection.contact is not None:
                    contact = connection.contact
                else:
                    contact = Contact.objects.create(name=name)
                connection.contact = contact
                connection.save()

                contact.name = name
                contact.language = language
                contact.gender = gender
                contact.birthdate = birth_date
                contact.reporting_location = district
                contact.occupation = occupation
                contact.village_name = village_name
                contact.groups.add(group)
                contact.save()
            except UploadContactException, e:
                with_error.append((row, e))
                continue
        print "With Error -", with_error
        self.unprocessed = str(with_error)
        self.processed_on = datetime.datetime.now()
        self.save()

    def _get_district(self, district):
        try:
            district = Location.objects.get(name__iexact=district, type__name='district')
            return district
        except Location.DoesNotExist:
            raise UploadContactException("District Name %s does not exist" % district)

    def _clean_phone(self, phone):
        num = phone.strip().replace('+', '').replace('-', '').replace(" ", '')
        if num.startswith('0'):
            num = '256' + num[1:]
        if num.startswith('7') or num.startswith('4') or num.startswith('3'):
            num = '256' + num
        if len(num) == 12 and num.startswith('256'):
            return num
        raise UploadContactException("Phone number %s is invalid" % phone)

    def _birth_date(self, age):
        try:
            return datetime.datetime.now() - relativedelta(years=int(age))
        except:
            raise UploadContactException("Age %s is invalid" % age)

    def _get_gender(self, gender):
        if gender.lower().startswith("m"):
            return "m"
        elif gender.lower().startswith("f"):
            return "f"
        raise UploadContactException("Gender %s is invalid" % gender)

    def _get_group(self, group):
        try:
            return Group.objects.get(name=group)
        except Group.DoesNotExist:
            raise UploadContactException("Group %s does not exist" % group)


class FlagTracker(models.Model):
    message = models.ForeignKey(Message, related_name="flag_track")
    response = models.ForeignKey(Message, related_name="response_track", null=True)
    reply = models.ForeignKey(Message, related_name="reply_track")
    user = models.ForeignKey(User)
    flag = models.ForeignKey(Flag)

    def __unicode__(self):
        return self.reply.text

    class Meta:
        app_label = 'ureport'