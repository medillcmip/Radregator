from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import urllib2
import urlparse
from urllib2 import HTTPError
from urllib2 import URLError
from BeautifulSoup import BeautifulSoup

import forms
import models


def get_page(url):
    """
    return formatted html 
    basically have to check for relative URLs in img's, css, scripts, etc
    at some point we may want to trim page down into text
    http://www.voidspace.org.uk/python/articles/urllib2.shtml
    """
    try:
        #TODO:append the paths for css to our head
        #TODO:check path's for relative and make absolute
        response = urllib2.urlopen(url)
        page = BeautifulSoup(response)
        return page.body
    except URLError, e:
        #TODO:Add more exception handling
        print e.reason


def clipper_submit_select(request):
   pass 

def create_article(url):
    #ok got the page back lets create an article
    #TODO:prolly need to break up logic for parsing to get all
    #fields necessary for an Article object
    url_o = urlparse.urlparse(url)
    try:
        newsorg = models.NewsOrganization.objects.get(name=url_o[1])
    except models.NewsOrganization.DoesNotExist:
        newsorg = models.NewsOrganization(url=url,name=url_o[1])
        newsorg.save()
    newarticle = models.Article(url=url, news_organization=newsorg,\
        source=newsorg)
    newarticle.save()

def clipper_paste_url(request):
    """
    grab an html page (or holla back if the input was too rough)
    and fuck that baby up, and spit it out on a new page so the 
    user can start selecting text inside our site
    """
    template_dict = {}
    form = None
    return_page = 'clipper.html'
    if request.method == 'POST':
        form = forms.UrlSubmitForm(request.POST)
        if form.is_valid():
            #start parsing out the page and get ready to forward us onto 
            url = form.cleaned_data['urlfield']
            form = forms.ClipTextForm()
            create_article(url)
            template_dict['requested_page'] = get_page(url)
            template_dict['url'] = url
            return_page = 'clipper_select_text.html'
    else: #first time we hit the page
        form = UrlSubmitForm()
    template_dict['form'] = form
    return render_to_response(return_page,template_dict,\
        context_instance=RequestContext(request))
