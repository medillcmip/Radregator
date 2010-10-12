from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from clipper.models import Article
from tagger.models import Tag

class Topic(models.Model):
    topic_tags = models.ManyToManyField("Tag", null=True) 
    title = models.CharField(max_length=80) 
    curators = models.ManyToManyField("UserProfile")

class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(UserProfile)
    tags = models.ManyToManyField("Tag", null=True) 
    related = models.ManyToManyField("self", through="CommentRelation", symmetrical=False, null=True)
    # see http://docs.djangoproject.com/en/1.2./topics/db/models/#extra-fields-on-many-to-many-relationships
    sites = models.ManyToManyField("Site")
    comment_type = models.ForeignKey("CommentType")
    topics = models.ManyToManyField("Topic")

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    facebook_user_id = models.TextField()

class CommentType(models.Model):
    name = models.CharField(max_length=15)

class CommentRelation(models.Model):
    left_comment = models.ForeignKey(Comment)
    right_comment = models.ForeignKey(Comment)
    relation_type = models.CharField(max_length=15)
