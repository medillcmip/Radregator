# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Summary'
        db.create_table('core_summary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(unique=True, blank=True)),
        ))
        db.send_create_signal('core', ['Summary'])

        # Adding model 'Topic'
        db.create_table('core_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('summary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Summary'])),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Topic'])

        # Adding M2M table for field topic_tags on 'Topic'
        db.create_table('core_topic_topic_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm['core.topic'], null=False)),
            ('tag', models.ForeignKey(orm['tagger.tag'], null=False))
        ))
        db.create_unique('core_topic_topic_tags', ['topic_id', 'tag_id'])

        # Adding M2M table for field curators on 'Topic'
        db.create_table('core_topic_curators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm['core.topic'], null=False)),
            ('userprofile', models.ForeignKey(orm['users.userprofile'], null=False))
        ))
        db.create_unique('core_topic_curators', ['topic_id', 'userprofile_id'])

        # Adding M2M table for field articles on 'Topic'
        db.create_table('core_topic_articles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm['core.topic'], null=False)),
            ('article', models.ForeignKey(orm['clipper.article'], null=False))
        ))
        db.create_unique('core_topic_articles', ['topic_id', 'article_id'])

        # Adding model 'Comment'
        db.create_table('core_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['users.UserProfile'])),
            ('comment_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.CommentType'])),
            ('is_parent', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Comment'])

        # Adding M2M table for field sources on 'Comment'
        db.create_table('core_comment_sources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('comment', models.ForeignKey(orm['core.comment'], null=False)),
            ('userprofile', models.ForeignKey(orm['users.userprofile'], null=False))
        ))
        db.create_unique('core_comment_sources', ['comment_id', 'userprofile_id'])

        # Adding M2M table for field tags on 'Comment'
        db.create_table('core_comment_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('comment', models.ForeignKey(orm['core.comment'], null=False)),
            ('tag', models.ForeignKey(orm['tagger.tag'], null=False))
        ))
        db.create_unique('core_comment_tags', ['comment_id', 'tag_id'])

        # Adding M2M table for field sites on 'Comment'
        db.create_table('core_comment_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('comment', models.ForeignKey(orm['core.comment'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('core_comment_sites', ['comment_id', 'site_id'])

        # Adding M2M table for field topics on 'Comment'
        db.create_table('core_comment_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('comment', models.ForeignKey(orm['core.comment'], null=False)),
            ('topic', models.ForeignKey(orm['core.topic'], null=False))
        ))
        db.create_unique('core_comment_topics', ['comment_id', 'topic_id'])

        # Adding model 'CommentType'
        db.create_table('core_commenttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('core', ['CommentType'])

        # Adding model 'CommentRelation'
        db.create_table('core_commentrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('left_comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['core.Comment'])),
            ('right_comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['core.Comment'])),
            ('relation_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('core', ['CommentRelation'])

        # Adding model 'CommentResponse'
        db.create_table('core_commentresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Comment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.UserProfile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['CommentResponse'])


    def backwards(self, orm):
        
        # Deleting model 'Summary'
        db.delete_table('core_summary')

        # Deleting model 'Topic'
        db.delete_table('core_topic')

        # Removing M2M table for field topic_tags on 'Topic'
        db.delete_table('core_topic_topic_tags')

        # Removing M2M table for field curators on 'Topic'
        db.delete_table('core_topic_curators')

        # Removing M2M table for field articles on 'Topic'
        db.delete_table('core_topic_articles')

        # Deleting model 'Comment'
        db.delete_table('core_comment')

        # Removing M2M table for field sources on 'Comment'
        db.delete_table('core_comment_sources')

        # Removing M2M table for field tags on 'Comment'
        db.delete_table('core_comment_tags')

        # Removing M2M table for field sites on 'Comment'
        db.delete_table('core_comment_sites')

        # Removing M2M table for field topics on 'Comment'
        db.delete_table('core_comment_topics')

        # Deleting model 'CommentType'
        db.delete_table('core_commenttype')

        # Deleting model 'CommentRelation'
        db.delete_table('core_commentrelation')

        # Deleting model 'CommentResponse'
        db.delete_table('core_commentresponse')


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
            'comment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.CommentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_parent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Comment']", 'null': 'True', 'through': "orm['core.CommentRelation']", 'symmetrical': 'False'}),
            'responses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'responses'", 'null': 'True', 'through': "orm['core.CommentResponse']", 'to': "orm['users.UserProfile']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False', 'blank': 'True'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sourced_comments'", 'blank': 'True', 'to': "orm['users.UserProfile']"}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'})
        },
        'core.topic': {
            'Meta': {'object_name': 'Topic'},
            'articles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['clipper.Article']", 'symmetrical': 'False', 'blank': 'True'}),
            'curators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.UserProfile']", 'symmetrical': 'False'}),
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
