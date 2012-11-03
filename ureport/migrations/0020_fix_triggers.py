# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        view_sql="""


DROP VIEW CONTACTS_EXPORT;CREATE VIEW CONTACTS_EXPORT AS SELECT   CONTACT.ID AS ID,CONTACT.NAME AS NAME, (SELECT DISTINCT COUNT(*) FROM RAPIDSMS_HTTPROUTER_MESSAGE WHERE
 RAPIDSMS_HTTPROUTER_MESSAGE.DIRECTION ='I'  AND RAPIDSMS_HTTPROUTER_MESSAGE.CONNECTION_ID = ( SELECT RAPIDSMS_CONNECTION.ID FROM RAPIDSMS_CONNECTION WHERE
 RAPIDSMS_CONNECTION.CONTACT_ID = CONTACT.ID  LIMIT 1 ) ) AS INCOMING,(SELECT DISTINCT COUNT(POLL_POLL_CONTACTS.ID) FROM POLL_POLL_CONTACTS WHERE
   POLL_POLL_CONTACTS.CONTACT_ID=CONTACT.ID GROUP BY POLL_POLL_CONTACTS.CONTACT_ID) AS QUESTIONS,(SELECT COUNT(POLL_RESPONSE.ID) FROM POLL_RESPONSE WHERE
    POLL_RESPONSE.CONTACT_ID=CONTACT.ID) AS RESPONSES,(SELECT MESSAGE.TEXT  FROM RAPIDSMS_HTTPROUTER_MESSAGE AS MESSAGE JOIN POLL_RESPONSE AS RESPONSE  ON
    RESPONSE.MESSAGE_ID= MESSAGE.ID
     WHERE
    POLL_ID=121   AND HAS_ERRORS='F' AND RESPONSE.CONTACT_ID=CONTACT.ID LIMIT 1) AS SOURCE,CONTACT.IS_CAREGIVER,CONTACT.REPORTING_LOCATION_ID,CONTACT.USER_ID ,
    CONNECTION.IDENTITY AS MOBILE,CONTACT.LANGUAGE ,DATE(SCRIPTSESSION.START_TIME) AS AUTOREG_JOIN_DATE ,EXTRACT(YEAR FROM AGE(CONTACT.BIRTHDATE)) AS AGE,
    CONTACT.GENDER, CONTACT.HEALTH_FACILITY AS FACILITY ,LOCATION.NAME AS DISTRICT,CONNECTION.ID AS CONNECTION_PK,UNREGISTER.QDATE AS QUIT_DATE,VILLAGES.VNAME
    AS VILLAGE ,(SELECT ARRAY_TO_STRING(ARRAY(SELECT NAME FROM AUTH_GROUP AS "GROUP" INNER JOIN  RAPIDSMS_CONTACT_GROUPS ON
      "GROUP".ID = RAPIDSMS_CONTACT_GROUPS.GROUP_ID
		WHERE  RAPIDSMS_CONTACT_GROUPS.CONTACT_ID = CONTACT.ID),', ')) AS "GROUP" FROM RAPIDSMS_CONTACT CONTACT  JOIN RAPIDSMS_CONNECTION CONNECTION ON
		CONNECTION.CONTACT_ID = CONTACT.ID LEFT JOIN SCRIPT_SCRIPTSESSION SCRIPTSESSION ON
		SCRIPTSESSION.CONNECTION_ID = CONNECTION.ID LEFT JOIN LOCATIONS_LOCATION LOCATION ON
		CONTACT.REPORTING_LOCATION_ID = LOCATION.ID  LEFT JOIN (SELECT MESSAGE.DATE AS QDATE,MESSAGE.ID AS MID FROM RAPIDSMS_HTTPROUTER_MESSAGE MESSAGE WHERE
		MESSAGE.DIRECTION = 'I' AND MESSAGE.APPLICATION = 'UNREGISTER') UNREGISTER ON
		UNREGISTER.MID = CONNECTION.ID  LEFT JOIN (SELECT LOCATIONS_LOCATION.NAME AS VNAME,LOCATIONS_LOCATION.ID AS VID  FROM LOCATIONS_LOCATION  ) VILLAGES ON
		VILLAGES.VID=CONTACT.VILLAGE_ID ;

        """
        materialized_view_sql="""
        drop table ureport_contact;
        create table ureport_contact as select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,contacts_export.group,
false as dirty,null::timestamp with time zone as expiry from contacts_export;


        """
        trigger="""


        CREATE OR REPLACE FUNCTION contact_trig_vw_facts_ins_upd_del() RETURNS trigger AS $$
        BEGIN
        IF (TG_OP = 'DELETE') THEN DELETE FROM ureport_contact AS c
        WHERE c.id = OLD.id;
        RETURN OLD; END IF;
        IF (TG_OP = 'INSERT') THEN
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,
        autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,
        connection_pk,ce.group  from contacts_export ce where ce.id = NEW.id;
         RETURN NEW;
        END IF;
        IF (TG_OP = 'UPDATE') THEN
        delete
        from ureport_contact uc
        where uc.id = NEW.id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,
        autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,
        connection_pk,ce.group  from contacts_export ce where ce.id = NEW.id;
        RETURN NEW;
        END IF; END;
        $$
        LANGUAGE plpgsql VOLATILE;

        CREATE OR REPLACE FUNCTION cgroups_trig_vw_facts_ins_upd_del() RETURNS trigger AS $$
        BEGIN
        IF (TG_OP = 'DELETE') THEN
        DELETE FROM ureport_contact AS c
        WHERE c.id = OLD.contact_id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,ce.group  from contacts_export ce where ce.id = OLD.contact_id;

        RETURN OLD; END IF;
        IF (TG_OP = 'INSERT') THEN
        DELETE FROM ureport_contact AS c
        WHERE c.id = NEW.contact_id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,ce.group  from contacts_export ce where ce.id = NEW.contact_id;
         RETURN NEW;
        END IF;
        IF (TG_OP = 'UPDATE') THEN
        DELETE FROM ureport_contact AS c
        WHERE c.id = NEW.contact_id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,ce.group  from contacts_export ce where ce.id = NEW.contact_id;

        RETURN NEW;
        END IF; END;
        $$
        LANGUAGE plpgsql VOLATILE;

        CREATE OR REPLACE FUNCTION response_trig_vw_facts_ins_upd_del() RETURNS trigger AS $$
        BEGIN
        IF (TG_OP = 'DELETE') THEN
        DELETE FROM ureport_contact AS c
        WHERE c.id = OLD.contact_id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,ce.group  from contacts_export ce where ce.id = OLD.contact_id;

        RETURN OLD; END IF;
        IF (TG_OP = 'INSERT') THEN
        DELETE FROM ureport_contact AS c
        WHERE c.id = NEW.contact_id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,ce.group  from contacts_export ce where ce.id = NEW.contact_id;
         RETURN NEW;
        END IF;
        IF (TG_OP = 'UPDATE') THEN
        DELETE FROM ureport_contact AS c
        WHERE c.id = NEW.contact_id;
        insert into ureport_contact  select id,name,is_caregiver,reporting_location_id ,user_id ,mobile ,language ,autoreg_join_date ,quit_date ,district ,age ,gender ,facility ,village  ,source ,responses ,questions ,incoming ,connection_pk,ce.group  from contacts_export ce where ce.id = NEW.contact_id;

        RETURN NEW;
        END IF; END;
        $$
        LANGUAGE plpgsql VOLATILE;

        CREATE TRIGGER contacts_ins_upd_del
        after  INSERT or   UPDATE or DELETE on  rapidsms_contact
        FOR EACH ROW EXECUTE PROCEDURE contact_trig_vw_facts_ins_upd_del();


        CREATE TRIGGER groupsc_ins_upd_del
        after  INSERT or   UPDATE or DELETE on  rapidsms_contact_groups
        FOR EACH ROW EXECUTE PROCEDURE cgroups_trig_vw_facts_ins_upd_del();


        CREATE TRIGGER response_ins_upd_del
        after  INSERT or   UPDATE or DELETE on poll_response
        FOR EACH ROW EXECUTE PROCEDURE response_trig_vw_facts_ins_upd_del();
        """
        db.execute(view_sql)
        db.execute(materialized_view_sql)
        db.execute(trigger)


    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Point']", 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': "orm['locations.LocationType']"})
        },
        'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'primary_key': 'True'})
        },
        'locations.point': {
            'Meta': {'object_name': 'Point'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'})
        },
        'poll.poll': {
            'Meta': {'ordering': "['-end_date']", 'object_name': 'Poll'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'polls'", 'symmetrical': 'False', 'to': "orm['rapidsms.Contact']"}),
            'default_response': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['rapidsms_httprouter.Message']", 'null': 'True', 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'response_type': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
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
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birthdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'health_facility': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_caregiver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reporting_location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Location']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'village': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'villagers'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'village_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'rapidsms_httprouter.message': {
            'Meta': {'object_name': 'Message'},
            'application': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'null': 'True', 'to': "orm['rapidsms_httprouter.MessageBatch']"}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['rapidsms.Connection']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_response_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'responses'", 'null': 'True', 'to': "orm['rapidsms_httprouter.Message']"}),
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
        'ureport.alertsexport': {
            'Meta': {'object_name': 'AlertsExport', 'db_table': "'alerts_export'"},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'forwarded': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'replied': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'details'", 'to': "orm['rapidsms_httprouter.Message']"}),
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True'})
        },
        'ureport.topresponses': {
            'Meta': {'object_name': 'TopResponses'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'top_responses'", 'to': "orm['poll.Poll']"}),
            'quote': ('django.db.models.fields.TextField', [], {}),
            'quoted': ('django.db.models.fields.TextField', [], {})
        },
        'ureport.ureportcontact': {
            'Meta': {'object_name': 'UreportContact', 'db_table': "'ureport_contact'"},
            'age': ('django.db.models.fields.IntegerField', [], {}),
            'autoreg_join_date': ('django.db.models.fields.DateField', [], {}),
            'connection_pk': ('django.db.models.fields.IntegerField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'facility': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incoming': ('django.db.models.fields.IntegerField', [], {}),
            'is_caregiver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'questions': ('django.db.models.fields.IntegerField', [], {}),
            'quit_date': ('django.db.models.fields.DateTimeField', [], {}),
            'reporting_location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Location']"}),
            'responses': ('django.db.models.fields.IntegerField', [], {}),
            'source': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'village': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['ureport']
    symmetrical = True
