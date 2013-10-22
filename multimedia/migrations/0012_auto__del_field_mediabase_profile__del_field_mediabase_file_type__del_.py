# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'MediaBase.profile'
        db.delete_column(u'multimedia_mediabase', 'profile')

        # Deleting field 'MediaBase.file_type'
        db.delete_column(u'multimedia_mediabase', 'file_type')

        # Deleting field 'MediaBase.user'
        db.delete_column(u'multimedia_mediabase', 'user_id')

        # Deleting field 'MediaBase.date_added'
        db.delete_column(u'multimedia_mediabase', 'date_added')

        # Deleting field 'MediaBase.date_modified'
        db.delete_column(u'multimedia_mediabase', 'date_modified')

        # Adding field 'MediaBase.created'
        db.add_column(u'multimedia_mediabase', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 22, 0, 0)),
                      keep_default=False)

        # Adding field 'MediaBase.modified'
        db.add_column(u'multimedia_mediabase', 'modified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 22, 0, 0)),
                      keep_default=False)

        # Adding field 'MediaBase.owner'
        db.add_column(u'multimedia_mediabase', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']),
                      keep_default=False)

        # Deleting field 'Video.auto_thumbnail'
        db.delete_column(u'multimedia_video', 'auto_thumbnail')

        # Deleting field 'Video.thumbnail_offset'
        db.delete_column(u'multimedia_video', 'thumbnail_offset')

        # Deleting field 'Video.generated_thumbnail'
        db.delete_column(u'multimedia_video', 'generated_thumbnail')

        # Deleting field 'Video.thumbnail_image'
        db.delete_column(u'multimedia_video', 'thumbnail_image_id')

        # Adding field 'Video.auto_thumb'
        db.add_column(u'multimedia_video', 'auto_thumb',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Video.auto_thumb_offset'
        db.add_column(u'multimedia_video', 'auto_thumb_offset',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=4, blank=True),
                      keep_default=False)

        # Adding field 'Video.custom_thumb'
        db.add_column(u'multimedia_video', 'custom_thumb',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'MediaBase.profile'
        raise RuntimeError("Cannot reverse this migration. 'MediaBase.profile' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'MediaBase.profile'
        db.add_column(u'multimedia_mediabase', 'profile',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'MediaBase.file_type'
        raise RuntimeError("Cannot reverse this migration. 'MediaBase.file_type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'MediaBase.file_type'
        db.add_column(u'multimedia_mediabase', 'file_type',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)

        # Adding field 'MediaBase.user'
        db.add_column(u'multimedia_mediabase', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'MediaBase.date_added'
        raise RuntimeError("Cannot reverse this migration. 'MediaBase.date_added' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'MediaBase.date_added'
        db.add_column(u'multimedia_mediabase', 'date_added',
                      self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'MediaBase.date_modified'
        raise RuntimeError("Cannot reverse this migration. 'MediaBase.date_modified' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'MediaBase.date_modified'
        db.add_column(u'multimedia_mediabase', 'date_modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True),
                      keep_default=False)

        # Deleting field 'MediaBase.created'
        db.delete_column(u'multimedia_mediabase', 'created')

        # Deleting field 'MediaBase.modified'
        db.delete_column(u'multimedia_mediabase', 'modified')

        # Deleting field 'MediaBase.owner'
        db.delete_column(u'multimedia_mediabase', 'owner_id')

        # Adding field 'Video.auto_thumbnail'
        db.add_column(u'multimedia_video', 'auto_thumbnail',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Video.thumbnail_offset'
        db.add_column(u'multimedia_video', 'thumbnail_offset',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=4, blank=True),
                      keep_default=False)

        # Adding field 'Video.generated_thumbnail'
        db.add_column(u'multimedia_video', 'generated_thumbnail',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Video.thumbnail_image'
        db.add_column(u'multimedia_video', 'thumbnail_image',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Video.auto_thumb'
        db.delete_column(u'multimedia_video', 'auto_thumb')

        # Deleting field 'Video.auto_thumb_offset'
        db.delete_column(u'multimedia_video', 'auto_thumb_offset')

        # Deleting field 'Video.custom_thumb'
        db.delete_column(u'multimedia_video', 'custom_thumb_id')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_files'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_filer.file_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filer_owned_folders'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image', '_ormbases': ['filer.File']},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['filer.File']", 'unique': 'True', 'primary_key': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'multimedia.audio': {
            'Meta': {'ordering': "(u'-created',)", 'object_name': 'Audio', '_ormbases': [u'multimedia.MediaBase']},
            u'mediabase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['multimedia.MediaBase']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'multimedia.mediabase': {
            'Meta': {'ordering': "(u'-created',)", 'object_name': 'MediaBase'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'encoded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'encoding': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uploaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'multimedia.video': {
            'Meta': {'ordering': "(u'-created',)", 'object_name': 'Video', '_ormbases': [u'multimedia.MediaBase']},
            'auto_thumb': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'auto_thumb_offset': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4', 'blank': 'True'}),
            'custom_thumb': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']", 'null': 'True', 'blank': 'True'}),
            u'mediabase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['multimedia.MediaBase']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['multimedia']