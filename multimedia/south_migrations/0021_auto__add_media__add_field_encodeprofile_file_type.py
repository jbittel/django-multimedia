# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Audio'
#        db.delete_table(u'multimedia_audio')

        # Removing M2M table for field profiles on 'Audio'
#        db.delete_table(db.shorten_name(u'multimedia_audio_profiles'))

        # Deleting model 'Video'
#        db.delete_table(u'multimedia_video')

        # Removing M2M table for field profiles on 'Video'
#        db.delete_table(db.shorten_name(u'multimedia_video_profiles'))

        # Remove all RemoteStorage objects to rebuild later
        orm.RemoteStorage.objects.all().delete()

        # Deleting field 'RemoteStorage.media_id'
        db.delete_column(u'multimedia_remotestorage', 'media_id')

        # Deleting field 'RemoteStorage.content_type'
        db.delete_column(u'multimedia_remotestorage', 'content_type_id')

        # Adding field 'RemoteStorage.media'
        db.add_column(u'multimedia_remotestorage', 'media',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['multimedia.Media']),
                      keep_default=False)

        # Adding model 'Media'
        db.create_table(u'multimedia_media', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'multimedia', ['Media'])

        # Adding M2M table for field profiles on 'Media'
        m2m_table_name = db.shorten_name(u'multimedia_media_profiles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('media', models.ForeignKey(orm[u'multimedia.media'], null=False)),
            ('encodeprofile', models.ForeignKey(orm[u'multimedia.encodeprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['media_id', 'encodeprofile_id'])

        # Adding field 'EncodeProfile.file_type'
        db.add_column(u'multimedia_encodeprofile', 'file_type',
                      self.gf('django.db.models.fields.CharField')(default='video', max_length=32),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Media'
        db.delete_table(u'multimedia_media')

        # Removing M2M table for field profiles on 'Media'
        db.delete_table(db.shorten_name(u'multimedia_media_profiles'))

        # Deleting field 'EncodeProfile.file_type'
        db.delete_column(u'multimedia_encodeprofile', 'file_type')


        # User chose to not deal with backwards NULL issues for 'RemoteStorage.media_id'
        raise RuntimeError("Cannot reverse this migration. 'RemoteStorage.media_id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'RemoteStorage.media_id'
        db.add_column(u'multimedia_remotestorage', 'media_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'RemoteStorage.content_type'
        raise RuntimeError("Cannot reverse this migration. 'RemoteStorage.content_type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'RemoteStorage.content_type'
        db.add_column(u'multimedia_remotestorage', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType']),
                      keep_default=False)

        # Deleting field 'RemoteStorage.media'
        db.delete_column(u'multimedia_remotestorage', 'media_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'multimedia.audio': {
            'Meta': {'object_name': 'Audio'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['multimedia.EncodeProfile']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'multimedia.encodeprofile': {
            'Meta': {'object_name': 'EncodeProfile'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'container': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'multimedia.media': {
            'Meta': {'ordering': "(u'-created',)", 'object_name': 'Media'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['multimedia.EncodeProfile']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'multimedia.remotestorage': {
            'Meta': {'object_name': 'RemoteStorage'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.Media']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.EncodeProfile']"})
        },
        u'multimedia.video': {
            'Meta': {'object_name': 'Video'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['multimedia.EncodeProfile']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['multimedia']
