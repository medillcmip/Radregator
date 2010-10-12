from django.db import models
from tagger.models import Tag
from core.models import UserProfile

class Article(models.Model):
    url = models.URLField(verify_exists=False) 
    news_organization = models.ForeignKey(NewsOrganization) 
    source = models.ForeignKey(NewsOrganization)
    authors = models.ManyToManyField("UserProfile") 
    title = models.CharField(max_length=200)

    # But we'll probably not be tagging articles initially, just aggregating tags from
    # related clips
    tags = models.ManyToManyField("Tag", null=True) 

class Clip(models.Model):
    tags = models.ManyToManyField("Tag", null=True) 
    article = models.ForeignKey(Article) 
    user = models.ForeignKey(UserProfile)
    text = models.TextField()

class NewsOrganization(models.Model):
    url = models.URLField(verify_exists=False) 
    name = models.CharField(max_length=80)
    users = models.ManyToManyField("UserProfile") 
