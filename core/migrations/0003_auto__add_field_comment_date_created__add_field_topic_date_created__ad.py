# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Comment.date_created'
        db.add_column('core_comment', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2010, 11, 2), blank=True), keep_default=False)

        # Adding field 'Topic.date_created'
        db.add_column('core_topic', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2010, 11, 2), blank=True), keep_default=False)

        # Adding field 'Summary.date_created'
        db.add_column('core_summary', 'date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2010, 11, 2), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Comment.date_created'
        db.delete_column('core_comment', 'date_created')

        # Deleting field 'Topic.date_created'
        db.delete_column('core_topic', 'date_created')

        # Deleting field 'Summary.date_created'
        db.delete_column('core_summary', 'date_created')


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
        'clipper.article': {
            'Meta': {'object_name': 'Article'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.UserProfile']", 'symmetrical': 'False'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'news_organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles_created'", 'to': "orm['clipper.NewsOrganization']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles_sourced'", 'to': "orm['clipper.NewsOrganization']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tagger.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'clipper.clip': {
            'Meta': {'object_name': 'Clip'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clipper.Article']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tagger.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.UserProfile']"}),
            'user_comments': ('django.db.models.fields.TextField', [], {})
        },
        'clipper.newsorganization': {
            'Meta': {'object_name': 'NewsOrganization'},
            'feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.UserProfile']", 'symmetrical': 'False'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.comment': {
            'Meta': {'object_name': 'Comment'},
            'clips': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['clipper.Clip']", 'null': 'True', 'blank': 'True'}),
            'comment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.CommentType']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_parent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Comment']", 'null': 'True', 'through': "orm['core.CommentRelation']", 'symmetrical': 'False'}),
            'responses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'responses'", 'null': 'True', 'through': "orm['core.CommentResponse']", 'to': "orm['users.UserProfile']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False', 'blank': 'True'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sourced_comments'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['users.UserProfile']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['tagger.Tag']", 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'comments'", 'blank': 'True', 'to': "orm['core.Topic']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['users.UserProfile']"})
        },
        'core.commentrelation': {
            'Meta': {'object_name': 'CommentRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['core.Comment']"}),
            'relation_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'right_comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['core.Comment']"})
        },
        'core.commentresponse': {
            'Meta': {'object_name': 'CommentResponse'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Comment']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.UserProfile']"})
        },
        'core.commenttype': {
            'Meta': {'object_name': 'CommentType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'core.summary': {
            'Meta': {'object_name': 'Summary'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'})
        },
        'core.topic': {
            'Meta': {'object_name': 'Topic'},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['clipper.Article']", 'symmetrical': 'False', 'blank': 'True'}),
            'curators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.UserProfile']", 'symmetrical': 'False'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'summary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Summary']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'topic_tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['tagger.Tag']", 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tagger.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80', 'db_index': 'True'})
        },
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'city': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_user_id': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'reporter_verified': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.UserProfile']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'street_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
