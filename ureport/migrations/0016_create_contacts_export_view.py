# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import datetime

class Migration(DataMigration):
    def forwards(self, orm):
        "Write your forwards methods here."
        year_now = datetime.datetime.now().year
        sql =\
        """   create or replace view contacts_export as SELECT
"rapidsms_contact"."id",
"rapidsms_contact"."name" as name,
(SELECT
"rapidsms_connection"."identity"
FROM
"rapidsms_connection"
WHERE
"rapidsms_connection"."contact_id" = "rapidsms_contact"."id"  LIMIT 1) as mobile,
"rapidsms_contact"."language",
(SELECT
DATE("script_scriptsession"."start_time")
FROM
"script_scriptsession"
INNER JOIN
"rapidsms_connection"
   ON (
      "script_scriptsession"."connection_id" = "rapidsms_connection"."id"
   )
WHERE
"rapidsms_connection"."contact_id" = "rapidsms_contact"."id"   LIMIT 1) as autoreg_join_date,
(SELECT
"rapidsms_httprouter_message"."date"
FROM
"rapidsms_httprouter_message"
WHERE
"rapidsms_httprouter_message"."direction" = 'I'
and "rapidsms_httprouter_message"."application" = 'unregister'
and  "rapidsms_httprouter_message"."connection_id" = (
   SELECT
      "rapidsms_connection"."id"
   FROM
      "rapidsms_connection"
   WHERE
      "rapidsms_connection"."contact_id" = "rapidsms_contact"."id"  LIMIT 1
) LIMIT 1
) as quit_date,                                 "locations_location"."name" as district,   (
%d-EXTRACT('year'
FROM
"rapidsms_contact"."birthdate")) as age,

"rapidsms_contact"."gender",
 "rapidsms_contact"."health_facility" as facility,
(SELECT
   "locations_location"."name"
FROM
   "locations_location"
WHERE
   "locations_location"."id"="rapidsms_contact"."village_id") as village,
(SELECT
   "auth_group"."name"
FROM
   "auth_group"
INNER JOIN
   "rapidsms_contact_groups"
      ON (
         "auth_group"."id" = "rapidsms_contact_groups"."group_id"
      )
WHERE
   "rapidsms_contact_groups"."contact_id" = "rapidsms_contact"."id" order by "auth_group"."id" desc  LIMIT 1) as
group,
(SELECT
"rapidsms_httprouter_message"."text"
FROM "rapidsms_httprouter_message"
JOIN "poll_response"
   ON "poll_response"."message_id"= "rapidsms_httprouter_message"."id"  where poll_id=121 and contact_id="rapidsms_contact"."id" and has_errors='f' limit 1) as source,
(SELECT
COUNT(*) FROM
   "poll_response"
WHERE
   "poll_response"."contact_id"="rapidsms_contact"."id") as responses,
   (SELECT DISTINCT
COUNT(*) FROM
   "poll_poll_contacts"
WHERE
   "poll_poll_contacts"."contact_id"="rapidsms_contact"."id" GROUP BY "poll_poll_contacts"."contact_id") as questions,

   (SELECT DISTINCT count(*)

FROM "rapidsms_httprouter_message"

WHERE  "rapidsms_httprouter_message"."direction" ='I'  and

"rapidsms_httprouter_message"."connection_id" = (
   SELECT
      "rapidsms_connection"."id"
   FROM
      "rapidsms_connection"
   WHERE
      "rapidsms_connection"."contact_id" = "rapidsms_contact"."id"  LIMIT 1
) ) as incoming

FROM
"rapidsms_contact"
LEFT JOIN
"locations_location"
   ON "rapidsms_contact"."reporting_location_id" = "locations_location"."id";
        """\
        % year_now

        db.execute(sql)


    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')",
                     'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
                'django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                           {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                     {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'locations.location': {
            'Meta': {'object_name': 'Location'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [],
                                {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [],
                          {'to': "orm['locations.Point']", 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [],
                                {'blank': 'True', 'related_name': "'children'", 'null': 'True',
                                 'to': "orm['locations.Location']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [],
                         {'blank': 'True', 'related_name': "'locations'", 'null': 'True',
                          'to': "orm['locations.LocationType']"})
        },
        'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': (
                'django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'primary_key': 'True'})
        },
        'locations.point': {
            'Meta': {'object_name': 'Point'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'})
        },
        'poll.poll': {
            'Meta': {'ordering': "['-end_date']", 'object_name': 'Poll'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [],
                             {'related_name': "'polls'", 'symmetrical': 'False', 'to': "orm['rapidsms.Contact']"}),
            'default_response': (
                'django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messages': ('django.db.models.fields.related.ManyToManyField', [],
                             {'to': "orm['rapidsms_httprouter.Message']", 'null': 'True', 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'response_type': ('django.db.models.fields.CharField', [],
                                  {'default': "'a'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'sites': (
                'django.db.models.fields.related.ManyToManyField', [],
                    {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'type': ('django.db.models.fields.SlugField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'rapidsms.backend': {
            'Meta': {'object_name': 'Backend'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'rapidsms.connection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'Connection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Backend']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [],
                            {'to': "orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birthdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                           {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'health_facility': (
                'django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_caregiver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reporting_location': ('django.db.models.fields.related.ForeignKey', [],
                                       {'to': "orm['locations.Location']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [],
                         {'blank': 'True', 'related_name': "'contact'", 'unique': 'True', 'null': 'True',
                          'to': "orm['auth.User']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                     {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'village': ('django.db.models.fields.related.ForeignKey', [],
                            {'blank': 'True', 'related_name': "'villagers'", 'null': 'True',
                             'to': "orm['locations.Location']"}),
            'village_name': (
                'django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'rapidsms_httprouter.message': {
            'Meta': {'object_name': 'Message'},
            'application': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'null': 'True',
                                                                         'to': "orm['rapidsms_httprouter.MessageBatch']"})
            ,
            'connection': ('django.db.models.fields.related.ForeignKey', [],
                               {'related_name': "'messages'", 'to': "orm['rapidsms.Connection']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_response_to': ('django.db.models.fields.related.ForeignKey', [],
                                   {'related_name': "'responses'", 'null': 'True',
                                    'to': "orm['rapidsms_httprouter.Message']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '10', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'rapidsms_httprouter.messagebatch': {
            'Meta': {'object_name': 'MessageBatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'ureport.autoreggrouprules': {
            'Meta': {'object_name': 'AutoregGroupRules'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'values': ('django.db.models.fields.TextField', [], {'default': 'None'})
        },
        'ureport.equatellocation': {
            'Meta': {'object_name': 'EquatelLocation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'segment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'ureport.ignoredtags': {
            'Meta': {'object_name': 'IgnoredTags'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Poll']"})
        },
        'ureport.messageattribute': {
            'Meta': {'object_name': 'MessageAttribute'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'db_index': 'True'})
        },
        'ureport.messagedetail': {
            'Meta': {'object_name': 'MessageDetail'},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ureport.MessageAttribute']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [],
                            {'related_name': "'details'", 'to': "orm['rapidsms_httprouter.Message']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'ureport.permit': {
            'Meta': {'object_name': 'Permit'},
            'allowed': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ureport.quotebox': {
            'Meta': {'object_name': 'QuoteBox'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {}),
            'quote': ('django.db.models.fields.TextField', [], {}),
            'quoted': ('django.db.models.fields.TextField', [], {})
        },
        'ureport.settings': {
            'Meta': {'object_name': 'Settings'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True'})
        },
        'ureport.topresponses': {
            'Meta': {'object_name': 'TopResponses'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [],
                         {'related_name': "'top_responses'", 'to': "orm['poll.Poll']"}),
            'quote': ('django.db.models.fields.TextField', [], {}),
            'quoted': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['ureport']
    symmetrical = True
