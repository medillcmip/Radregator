from django.db import models
from django.contrib.sites.models import Site
from radregator.clipper.models import Article
from radregator.tagger.models import Tag
from radregator.users.models import UserProfile


class Summary(models.Model):
    """Summary of a subject (likely a Topic).  Make this a separate class
       if we want to do versioning."""
    text = models.TextField(blank=True, unique = True)
    
    def __unicode__(self):
        return self.text[:80]

    class Meta:
        verbose_name_plural = 'Summaries'

class Topic(models.Model):
    """A subject of discussion.  An information silo.  These will generally
       correspond to a page on the front end that will aggregate
       comments and other content around the subject.  This might
       be something like 'Evanston Libraries'

       Fields:

       short_title: A shortened, space-replaced, weird character cleaned 
                    version of the title.  This will get used in the URL
                    paths to views related to a given topic.
       topic_tags: Content with any of these tags can get pulled into a topic 
                   view.
       curators: Users who have priveleges to update this topic.
       summary: Short (1-2) paragraph description of the topic, maintained
                by one of the curators.
       articles: Articles (probably recent ones) to display on the front page, selected by curators. Probably ancestors of timeline."""
    title = models.CharField(max_length=80, unique = True) 
    short_title = models.SlugField(unique = True)
    summary = models.ForeignKey(Summary)
    topic_tags = models.ManyToManyField(Tag, null=True, blank=True) 
    curators = models.ManyToManyField(UserProfile)
    articles = models.ManyToManyField(Article, blank=True)

    def __unicode__(self):
        return self.title
    
    
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
    tags = models.ManyToManyField(Tag, null=True, blank=True) 
    related = models.ManyToManyField("self", through="CommentRelation", 
                                     symmetrical=False, null=True)
    sites = models.ManyToManyField(Site, blank=True)
    comment_type = models.ForeignKey("CommentType")
    topics = models.ManyToManyField("Topic", blank=True, related_name = 'comments')
    responses = models.ManyToManyField("UserProfile", through="CommentResponses", 
                                       symmetrical=False, null=True)

    def __unicode__(self):
        return self.text[:80]

class CommentType(models.Model):
    """Type of comment, e.g. question, concern, answer ...  This is a separate
       class so we can easily add new types of comments."""
    name = models.CharField(max_length=15)

    def __unicode__(self):
        return self.name

class CommentRelation(models.Model):
    """Extra information about the relationship between two comments.
    see http://docs.djangoproject.com/en/1.2./topics/db/models/#extra-fields-on-many-to-many-relationships"""
    left_comment = models.ForeignKey(Comment, related_name='+') 
    # Don't need to create an inverse relation
    right_comment = models.ForeignKey(Comment, related_name='+')
    # Don't need to create an inverse relation
    relation_type = models.CharField(max_length=15)

class CommentResponse(models.Model):
    """User response to a comment.

       These are responses that are not other comments.  This will
       implement the 'I also have this question' or 'I share this concern'
       functionality.  You can think of it as implementing Facebook 'like'
       style features."""

    COMMENT_RESPONSE_CHOICES = (
        ('share', 'I share this concern'),
        ('have', 'I have this question'),
        ('like', 'I like this'),
    )

    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(UserProfile)
    type = models.CharField(max_length=20, choices=COMMENT_RESPONSE_CHOICES)
