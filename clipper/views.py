from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import urllib2
import urlparse
from urllib2 import HTTPError
from urllib2 import URLError
from BeautifulSoup import BeautifulSoup, Tag
import re
import datetime
import core.models
import users.models
import clipper.forms
import clipper.models
import core.utils
import json 

logger = core.utils.get_logger()

relative_url_exp = re.compile("(src|href|action)\s*=\s*(\'|\"|(?!\"|\'))(?!(http:|ftp:|mailto:|https:|#))")
#a quick survey of sites indicates that many news organizations use a format
#much like this one to indicate who the article was written by
author_exp = re.compile("([Bb][Yy]:?-? ?)([A-Z][A-Z|a-z]* [A-Z][A-Z|a-z]*)")
date_exp = re.compile("")

class FileTypeNotSupported(Exception):
    """
    message = an error message describing the problem
    mimetype_msg = an instance of the mimetype.Message class as returned
        by the urllib2 response object
    """
    def __init__(self, message, mimetype_msg):
        self.message = message
        self.mimetype_msg = mimetype_msg
    def __str__(self):
        return repr(self.message)

def get_article_meta(page):
    """
    get a beautiful soup page and start mining it for meta data about an 
    article then save that shit

    return ret_val - a dictionary with keys title, author, and date
    """
    ret_val = dict()
    #try to get the title
    try:
        #looks like most article titles can be found in the page's title
        #not certain for everything
        title = page.html.head.title.string
    except Exception as e:
        logger.debug('get_article_meta(page, article): REASON=' + str(e))
        title = ''

    ret_val['title'] = title
    #look for the author
    total_str = ''.join(page.findAll(text=True))
    #total_str = ''.join(page.html.body.findAll(text=author_exp))
    match = author_exp.search(total_str)
    if match:
        author = match.group(2)
    else:
        author = ''
    #look for the dates, yikes!
    
    ret_val['author'] = author
    ret_val['date'] = ''
    return ret_val

def get_page(url):
    """
    return formatted html 
    get meta data about the article
    basically have to check for relative URLs in img's, css, scripts, etc
    at some point we may want to trim page down into text
    http://www.voidspace.org.uk/python/articles/urllib2.shtml

    need to return a dictionary full of meta-data about the article and
    its page to display
    """
    response = urllib2.urlopen(url)
    if response.info().gettype() != 'text/html':
        raise FileTypeNotSupported("Currently, we only support HTML files"+\
            ".  This one appears to be a '%s'" \
            %(response.info().gettype()), response.info())
    page = BeautifulSoup(response)
    ret_val = get_article_meta(page)
    url_o = urlparse.urlparse(url)
    scripts = page.findAll('script')
    #remove all scripts so we can use the ones on our site to scrape
    #the users selection... any ideas on how to remove a whole subtree?
    for i in scripts:
        i.extract()
    #get_article_meta(page,article)
    #get all the elements we want to make absolute
    script_tags = page.findAll(['a','img','link','href'])
    for idx, ele in enumerate(script_tags):
        match =  relative_url_exp.split(ele.prettify())
        #for i,m in enumerate(match):
        #    print i,m
        if len(match) > 1:
            path = re.split("\"", match[4])
            new_str = url_o[0] + "://" + url_o[1] +'/'+ path[0]
            ele[match[1]] = new_str
        else:
            pass

    #lets kill the tags we no longer need
    
    ret_val['page_body'] = page.html.body.renderContents()
    ret_val['page_head'] = page.html.head.renderContents()
    return ret_val

def create_author(name):
    """
    i expect the name to be 'FIRST<space>LAST' though this isn't guaranteed
    """
    baseuser = None
    ouruser = None
    try:
        baseuser = users.models.User.objects.get(username=name)
    except users.models.User.DoesNotExist:
        first = ''
        last = ''
        first_n_last = name.split(' ')
        if len(first_n_last) > 1:
            first = first_n_last[0]
            last = first_n_last[1]
        baseuser = users.models.User.objects.create_user(username=name, password='',email='na')
        baseuser.first_name = first
        baseuser.last_name = last
        baseuser.save()
    try:
        ouruser =  users.models.UserProfile.objects.get(user=baseuser)
    except users.models.UserProfile.DoesNotExist:
        ouruser = users.models.UserProfile(user=baseuser, user_type='A')
        ouruser.save()
    return ouruser

@login_required()
def clipper_submit_select(request):
    template_dict = {} 
    if request.method == 'POST':
        form = clipper.forms.ClipTextForm(request.POST)
        if form.is_valid():
            logger.debug('clipper_submit_selection(request): form is valid')
            url = form.cleaned_data['url_field']
            selected_text = form.cleaned_data['selected_text']
            comment_text = form.cleaned_data['user_comments']
            title = form.cleaned_data['title']
            author_name = form.cleaned_data['author']
            date_published = form.cleaned_data['date_published']
            user = users.models.UserProfile.objects.get(user=request.user)
            try:
                comment = core.models.Comment.objects.get(id=form.cleaned_data['comment_id_field'])
                the_article = clipper.models.Article.objects.get(url=url)
                author = create_author(author_name)
                the_article.authors.add(author)
                the_article.title = title
                the_article.date_published = date_published
                the_article.save()
                the_clip = clipper.models.Clip(article=the_article, \
                    text = selected_text, user=user, user_comments=comment_text)
                the_clip.save()
                comment.clips.add(the_clip)
                comment.save()
                return HttpResponseRedirect('/')
            except clipper.models.Article.DoesNotExist, e:
                logger.debug('clipper_submit_selection(request): type='+\
                            str(type(e)) + ' ,REASON=' + str(e))
            except core.models.Comment.DoesNotExist, e:
                logger.debug('clipper_submit_selection(request): type='+\
                            str(type(e)) + ' ,REASON=' + str(e))
        else:
            template_dict['form'] = form
            return render_to_response('clipper_select_text.html',template_dict,\
                context_instance=RequestContext(request))
    #TODO: need to figure out how to deal with the case that people just landed 
    #here without going through the workflow
    logger.debug('clipper_submit_selection(request): returning 404, fell into bad block')
    return HttpResponseRedirect('/404.html')

def create_article(url):
    #ok got the page back lets create an article
    #TODO:prolly need to break up logic for parsing to get all
    #fields necessary for an Article object

    url_o = urlparse.urlparse(url)
    try:
        news_org = clipper.models.NewsOrganization.objects.get(name=url_o[1])
    except clipper.models.NewsOrganization.DoesNotExist, e:
        logger.debug('create_article(url): type=' + str(type(e)) +\
                    ' ,REASON=' + str(e)+ ' ,URL='+url)
        news_org = clipper.models.NewsOrganization(url=url,name=url_o[1])
        news_org.save()
    try:
        the_article = clipper.models.Article.objects.get(url=url)
    except clipper.models.Article.DoesNotExist, e:
        logger.debug('create_article(url): type=' + str(type(e)) +\
                    ' ,REASON=' +str(e) + ' ,URL='+url)
        the_article = clipper.models.Article(url=url, news_organization=news_org,\
            source=news_org)
        the_article.save()

@login_required()
def clipper_paste_url(request, comment_id, user_comments, url_field):
    """
    grab an html page (or holla back if the input was too rough)
    and fuck that baby up, and spit it out on a new page so the 
    user can start selecting text inside our site
    """
    print url_field
    print user_comments
    template_dict = {}
    form = None
    return_page = 'clipper.html'
    if request.method == 'GET':
        url = url_field
        if not url.startswith('http://'):
            url = 'http://'+url
        try:
            values = get_page(url)
            template_dict['requested_page_body'] = values['page_body']
            template_dict['requested_page_head'] = values['page_head']
            template_dict['url'] = url
            form = clipper.forms.ClipTextForm(initial={'url_field': url,\
                 'comment_id_field': comment_id, 'title': values['title'],\
                'author': values['author'], 'user_comments': user_comments})
            return_page = 'clipper_select_text.html'
        except FileTypeNotSupported as fns:
            logger.debug('clipper_paste_url(request, comment_id): TYPE=' + str(type(fns)) +\
                ', REASON=' + str(fns) + ', URL=' + url)
            template_dict['errors'] = str(fns) + "  Please try another url."
        except Exception as ex:
            logger.debug('clipper_paste_url(request, comment_id): type=' + str(type(ex)) +\
                         ' ,REASON='+ str(ex) +',URL=' + url)
            template_dict['errors'] = str(ex)
    elif request.method == 'POST':
        form = clipper.forms.UrlSubmitForm(request.POST)
        if form.is_valid():
            #start parsing out the page and get ready to forward us onto 
            url = form.cleaned_data['url_field']
            article = create_article(url)
            #html to output on the next page
            try:
                values = get_page(url)
                template_dict['requested_page_body'] = values['page_body']
                template_dict['requested_page_head'] = values['page_head']
                template_dict['url'] = url
                form = clipper.forms.ClipTextForm(initial={'url_field': url,\
                     'comment_id_field': comment_id, 'title': values['title'],\
                    'author': values['author']})
                return_page = 'clipper_select_text.html'
            except FileTypeNotSupported as fns:
                logger.debug('clipper_paste_url(request, comment_id): TYPE=' + str(type(fns)) +\
                    ', REASON=' + str(fns) + ', URL=' + url)
                template_dict['errors'] = str(fns) + "  Please try another url."
            except Exception as ex:
                logger.debug('clipper_paste_url(request, comment_id): type=' + str(type(ex)) +\
                             ' ,REASON='+ str(ex) +',URL=' + url)
                template_dict['errors'] = str(ex)
    else: #first time we hit the page
        form = clipper.forms.UrlSubmitForm()
    template_dict['form'] = form
    return render_to_response(return_page,template_dict,\
        context_instance=RequestContext(request))


@login_required()
def api_clipper_submit(request, output_format='json'):
    """Like clipper_submit_select but through AJAX"""
    data = {} # Response data 
    status = 200 # Ok
    try:
        if request.is_ajax():
            if request.method == 'POST':
                form = clipper.forms.ClipTextForm(request.POST)
                if form.is_valid():
                    logger.debug('clipper_submit_selection(request): form is valid')
                    url = form.cleaned_data['url_field']
                    selected_text = form.cleaned_data['selected_text']
                    comment_text = form.cleaned_data['user_comments']
                    title = form.cleaned_data['title']
                    author_name = form.cleaned_data['author']
                    date_published = form.cleaned_data['date_published']
                    user = users.models.UserProfile.objects.get(user=request.user)
                    try:
                        comment = core.models.Comment.objects.get(id=form.cleaned_data['comment_id_field'])
                        the_article = clipper.models.Article.objects.get(url=url)
                        author = create_author(author_name)
                        the_article.authors.add(author)
                        the_article.title = title
                        the_article.date_published = date_published
                        the_article.save()
                        the_clip = clipper.models.Clip(article=the_article, \
                            text = selected_text, user=user, user_comments=comment_text)
                        the_clip.save()
                        comment.clips.add(the_clip)
                        comment.save()

                    except clipper.models.Article.DoesNotExist, e:
                        logger.debug('clipper_submit_selection(request): type='+\
                                    str(type(e)) + ' ,REASON=' + str(e))
                        data['error'] = "%s" % e
                    except core.models.Comment.DoesNotExist, e:
                        logger.debug('clipper_submit_selection(request): type='+\
                                    str(type(e)) + ' ,REASON=' + str(e))
                        data['error'] = "%s" % e
                else:
                    # Form didn't validate
                    #template_dict['form'] = form
                    #return render_to_response('clipper_select_text.html',template_dict,\
                    #   context_instance=RequestContext(request))
                    print form.errors.keys()
        
                    status = 400 # Bad Request
                    data['error'] = "Some required fields are missing"
                    data['field_errors'] = form.errors
                    data['error_html'] = core.utils.build_readable_errors(form.errors)

            else:
                # Method not POST
                raise MethodUnsupported("This endpoint only accepts POSTs.")
        else:
            # Non-AJAX request.  Disallow for now.
            raise NonAjaxRequest( \
                "Remote API calls aren't allowed right now. " + \
                "This might change some day.")

    except NonAjaxRequest, e:
        status = 403 # Forbidden
        data['error'] = "%s" % e

    except MethodUnsupported, error:
        status = 405 # Method not allowed
        data['error'] = "%s" % error


    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)

