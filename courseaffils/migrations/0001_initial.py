# flake8: noqa
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Course'
        db.create_table('courseaffils_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('faculty_group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='faculty_of', null=True, to=orm['auth.Group'])),
        ))
        db.send_create_signal('courseaffils', ['Course'])

        # Adding model 'CourseSettings'
        db.create_table('courseaffils_coursesettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.OneToOneField')(related_name='settings', unique=True, to=orm['courseaffils.Course'])),
            ('custom_headers', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('courseaffils', ['CourseSettings'])

        # Adding model 'CourseInfo'
        db.create_table('courseaffils_courseinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.OneToOneField')(related_name='info', unique=True, to=orm['courseaffils.Course'])),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('starttime', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('endtime', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('days', self.gf('django.db.models.fields.CharField')(max_length=7, null=True, blank=True)),
        ))
        db.send_create_signal('courseaffils', ['CourseInfo'])

        # Adding model 'CourseDetails'
        db.create_table('courseaffils_coursedetails', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['courseaffils.Course'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('courseaffils', ['CourseDetails'])


    def backwards(self, orm):
        
        # Deleting model 'Course'
        db.delete_table('courseaffils_course')

        # Deleting model 'CourseSettings'
        db.delete_table('courseaffils_coursesettings')

        # Deleting model 'CourseInfo'
        db.delete_table('courseaffils_courseinfo')

        # Deleting model 'CourseDetails'
        db.delete_table('courseaffils_coursedetails')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'courseaffils.course': {
            'Meta': {'object_name': 'Course'},
            'faculty_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'faculty_of'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'courseaffils.coursedetails': {
            'Meta': {'object_name': 'CourseDetails'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courseaffils.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'courseaffils.courseinfo': {
            'Meta': {'object_name': 'CourseInfo'},
            'course': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'info'", 'unique': 'True', 'to': "orm['courseaffils.Course']"}),
            'days': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'endtime': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'starttime': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'courseaffils.coursesettings': {
            'Meta': {'object_name': 'CourseSettings'},
            'course': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'settings'", 'unique': 'True', 'to': "orm['courseaffils.Course']"}),
            'custom_headers': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['courseaffils']
