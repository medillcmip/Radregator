# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Article'
        db.create_table('clipper_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('news_organization', self.gf('django.db.models.fields.related.ForeignKey')(related_name='articles_created', to=orm['clipper.NewsOrganization'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='articles_sourced', to=orm['clipper.NewsOrganization'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('clipper', ['Article'])

        # Adding M2M table for field authors on 'Article'
        db.create_table('clipper_article_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['clipper.article'], null=False)),
            ('userprofile', models.ForeignKey(orm['users.userprofile'], null=False))
        ))
        db.create_unique('clipper_article_authors', ['article_id', 'userprofile_id'])

        # Adding M2M table for field tags on 'Article'
        db.create_table('clipper_article_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['clipper.article'], null=False)),
            ('tag', models.ForeignKey(orm['tagger.tag'], null=False))
        ))
        db.create_unique('clipper_article_tags', ['article_id', 'tag_id'])

        # Adding model 'Clip'
        db.create_table('clipper_clip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clipper.Article'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.UserProfile'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('clipper', ['Clip'])

        # Adding M2M table for field tags on 'Clip'
        db.create_table('clipper_clip_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('clip', models.ForeignKey(orm['clipper.clip'], null=False)),
            ('tag', models.ForeignKey(orm['tagger.tag'], null=False))
        ))
        db.create_unique('clipper_clip_tags', ['clip_id', 'tag_id'])

        # Adding model 'NewsOrganization'
        db.create_table('clipper_newsorganization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('feed_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('clipper', ['NewsOrganization'])

        # Adding M2M table for field users on 'NewsOrganization'
        db.create_table('clipper_newsorganization_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newsorganization', models.ForeignKey(orm['clipper.newsorganization'], null=False)),
            ('userprofile', models.ForeignKey(orm['users.userprofile'], null=False))
        ))
        db.create_unique('clipper_newsorganization_users', ['newsorganization_id', 'userprofile_id'])


    def backwards(self, orm):
        
        # Deleting model 'Article'
        db.delete_table('clipper_article')

        # Removing M2M table for field authors on 'Article'
        db.delete_table('clipper_article_authors')

        # Removing M2M table for field tags on 'Article'
        db.delete_table('clipper_article_tags')

        # Deleting model 'Clip'
        db.delete_table('clipper_clip')

        # Removing M2M table for field tags on 'Clip'
        db.delete_table('clipper_clip_tags')

        # Deleting model 'NewsOrganization'
        db.delete_table('clipper_newsorganization')

        # Removing M2M table for field users on 'NewsOrganization'
        db.delete_table('clipper_newsorganization_users')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tagger.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.UserProfile']"})
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

    complete_apps = ['clipper']
