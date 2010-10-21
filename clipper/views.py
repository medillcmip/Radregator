from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import urllib2
import urlparse
from urllib2 import HTTPError
from urllib2 import URLError
from BeautifulSoup import BeautifulSoup

import core.models
import users.models
import clipper.forms
import clipper.models


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


@login_required()
def clipper_submit_select(request):
    template_dict = {} 
    if request.method == 'POST':
        form = clipper.forms.ClipTextForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url_field']
            selected_text = form.cleaned_data['selected_text']
            user = users.models.UserProfile.objects.get(user=request.user)
            try:
                comment = core.models.Comment.objects.get(id=form.cleaned_data['comment_id_field'])
                the_article = clipper.models.Article.objects.get(url=url)
                the_clip = clipper.models.Clip(article=the_article, \
                    text = selected_text, user=user)
                the_clip.save()
                comment.clips.add(the_clip)
                comment.save()
                return HttpResponseRedirect('/')
            except clipper.models.Article.DoesNotExist, e:
               print 'clipper_submit_select(request): ' + str(e)
            except core.models.Comment.DoesNotExist, e:
               print 'clipper_submit_select(request): ' + str(e)
        else:
            template_dict['form'] = form
            return render_to_response('clipper_select_text.html',template_dict,\
                context_instance=RequestContext(request))
    #TODO: need to figure out how to deal with the case that people just landed 
    #here without going through the workflow
    return HttpResponseRedirect('/404.html')

def create_article(url):
    #ok got the page back lets create an article
    #TODO:prolly need to break up logic for parsing to get all
    #fields necessary for an Article object
    url_o = urlparse.urlparse(url)
    try:
        news_org = clipper.models.NewsOrganization.objects.get(name=url_o[1])
    except clipper.models.NewsOrganization.DoesNotExist, e:
        print 'create_article(): ' + str(e)
        news_org = clipper.models.NewsOrganization(url=url,name=url_o[1])
        news_org.save()
    try:
        the_article = clipper.models.Article.objects.get(url=url)
    except clipper.models.Article.DoesNotExist, e:
        print 'create_article(): ' + str(e)
        the_article = clipper.models.Article(url=url, news_organization=news_org,\
            source=news_org)
        the_article.save()

@login_required()
def clipper_paste_url(request, comment_id):
    """
    grab an html page (or holla back if the input was too rough)
    and fuck that baby up, and spit it out on a new page so the 
    user can start selecting text inside our site
    """
    template_dict = {}
    form = None
    return_page = 'clipper.html'
    if request.method == 'POST':
        form = clipper.forms.UrlSubmitForm(request.POST)
        if form.is_valid():
            #start parsing out the page and get ready to forward us onto 
            url = form.cleaned_data['url_field']
            create_article(url)
            #html to output on the next page
            template_dict['requested_page'] = get_page(url)
            template_dict['url'] = url
            form = clipper.forms.ClipTextForm(initial={'url_field': url,\
                 'comment_id_field': comment_id})
            return_page = 'clipper_select_text.html'
    else: #first time we hit the page
        form = clipper.forms.UrlSubmitForm()
    template_dict['form'] = form
    return render_to_response(return_page,template_dict,\
        context_instance=RequestContext(request))
