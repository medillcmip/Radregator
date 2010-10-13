from django.db import models
from radregator.tagger.models import Tag
from radregator.users.models import UserProfile

class Article(models.Model):
    """ A news article.  These will be the sources for answers. """
    url = models.URLField(verify_exists=False, unique = True) 
    news_organization = models.ForeignKey("NewsOrganization", related_name='articles_created') 
    source = models.ForeignKey("NewsOrganization", related_name = 'articles_sourced')
    authors = models.ManyToManyField(UserProfile) 
    title = models.CharField(max_length=200)

    # But we'll probably not be tagging articles initially, just aggregating tags from
    # related clips
    tags = models.ManyToManyField(Tag, null=True) 

    def __unicode__(self):
        return self.title

class Clip(models.Model):
    """ Relevent text from an article.  """
    tags = models.ManyToManyField(Tag, null=True) 
    article = models.ForeignKey(Article) 
    user = models.ForeignKey(UserProfile)
    text = models.TextField()

    def __unicode__(self):
        return self.text[:80]

class NewsOrganization(models.Model):
    """ A news organization that has produced an article. """
    url = models.URLField(verify_exists=False) 
    name = models.CharField(max_length=80)
    users = models.ManyToManyField(UserProfile) 
    feed_url = models.URLField(verify_exists=False) 

    def __unicode__(self):
        return self.name
