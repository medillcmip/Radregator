from django.db import models
from django.contrib.sites.models import Site
from radregator.clipper.models import Article
from radregator.tagger.models import Tag
from radregator.users.models import UserProfile


class Summary(models.Model):
    """Summary of a subject (likely a Topic).  Make this a separate class
       if we want to do versioning."""
    text = models.TextField()

class Topic(models.Model):
    """A subject of discussion.  An information silo.  These will generally
       correspond to a page on the front end that will aggregate
       comments and other content around the subject.  This might
       be something like 'Evanston Libraries'

       Fields:

       topic_tags: Content with any of these tags can get pulled into a topic 
                   view.
       curators: Users who have priveleges to update this topic.
       summary: Short (1-2) paragraph description of the topic, maintained
                by one of the curators."""
    title = models.CharField(max_length=80) 
    summary = models.ForeignKey(Summary)
    topic_tags = models.ManyToManyField(Tag, null=True) 
    curators = models.ManyToManyField(UserProfile)
    
class Comment(models.Model):
    """User-generated feedback to the system.  These will implement questions,
       answers, concerns and replies.

       Fields:

       related: Comments that are related to this comment, e.g. an answer to
                a question, a re-phrasing of a comment, a question about
                a comment, or something that is just conceptually related.
       sites: Sites which this content can appear on.  This is anticipating
              sharing content between multiple sites, e.g. a Chicago
              election site and an Evanston local news site.
       comment_type: Question, concern, respsonse ...
       topics: Topics to which this comment relates."""
    text = models.TextField()
    user = models.ForeignKey(UserProfile)
    tags = models.ManyToManyField(Tag, null=True) 
    related = models.ManyToManyField("self", through="CommentRelation", symmetrical=False, null=True)
    sites = models.ManyToManyField(Site)
    comment_type = models.ForeignKey("CommentType")
    topics = models.ManyToManyField("Topic")


class CommentType(models.Model):
    """Type of comment, e.g. question, concern, answer ...  This is a separate
       class so we can easily add new types of comments."""
    name = models.CharField(max_length=15)

class CommentRelation(models.Model):
    """Extra information about the relationship between two comments.
    see http://docs.djangoproject.com/en/1.2./topics/db/models/#extra-fields-on-many-to-many-relationships"""
    left_comment = models.ForeignKey(Comment, related_name='+') 
    # Don't need to create an inverse relation
    right_comment = models.ForeignKey(Comment, related_name='+')
    # Don't need to create an inverse relation
    relation_type = models.CharField(max_length=15)
