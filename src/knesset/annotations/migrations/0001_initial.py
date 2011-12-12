# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AnnotationPermissions'
        db.create_table('annotations_annotationpermissions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('read', self.gf('knesset.annotations.models.CommaDelimitedStringListField')()),
            ('update', self.gf('knesset.annotations.models.CommaDelimitedStringListField')()),
            ('delete', self.gf('knesset.annotations.models.CommaDelimitedStringListField')()),
            ('admin', self.gf('knesset.annotations.models.CommaDelimitedStringListField')()),
        ))
        db.send_create_signal('annotations', ['AnnotationPermissions'])

        # Adding model 'Annotation'
        db.create_table('annotations_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotator_schema_version', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('account_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('knesset.annotations.models.DictField')(default={})),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('quote', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('ranges', self.gf('knesset.annotations.models.CommaDelimitedStringListField')()),
            ('permissions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.AnnotationPermissions'])),
        ))
        db.send_create_signal('annotations', ['Annotation'])


    def backwards(self, orm):
        
        # Deleting model 'AnnotationPermissions'
        db.delete_table('annotations_annotationpermissions')

        # Deleting model 'Annotation'
        db.delete_table('annotations_annotation')


    models = {
        'annotations.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'account_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'annotator_schema_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.AnnotationPermissions']"}),
            'quote': ('django.db.models.fields.TextField', [], {}),
            'ranges': ('knesset.annotations.models.CommaDelimitedStringListField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'user': ('knesset.annotations.models.DictField', [], {'default': '{}'})
        },
        'annotations.annotationpermissions': {
            'Meta': {'object_name': 'AnnotationPermissions'},
            'admin': ('knesset.annotations.models.CommaDelimitedStringListField', [], {}),
            'delete': ('knesset.annotations.models.CommaDelimitedStringListField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read': ('knesset.annotations.models.CommaDelimitedStringListField', [], {}),
            'update': ('knesset.annotations.models.CommaDelimitedStringListField', [], {})
        }
    }

    complete_apps = ['annotations']
