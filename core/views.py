from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator
from fbapi.facebook import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from radregator.users.models import UserProfile,User
from django.contrib.auth import authenticate, login, logout

from models import Topic,CommentType, Comment, Summary, CommentRelation
from radregator.tagger.models import Tag
from radregator.core.forms import CommentSubmitForm, CommentDeleteForm, TopicDeleteForm, NewTopicForm, MergeCommentForm
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from radregator.core.exceptions import UnknownOutputFormatException 
from django.core import serializers
from utils import slugify
from django.http import Http404

import logging

# Set up logging

# create logger
logger = logging.getLogger("radregator") 

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

if settings.DEBUG:
    # If we're in DEBUG mode, set log level to DEBUG
    logger.setLevel(logging.DEBUG) 

def reporterview(request):
    """ VERY rudimentary reporter view"""

    template_dict = {
        'commentdeleteform' : CommentDeleteForm(),
        'topicdeleteform' : TopicDeleteForm(),
        'newtopicform' : NewTopicForm(),
        'mergecommentform' : MergeCommentForm()
        }

    template_dict.update(csrf(request))

    return render_to_response('reporterview.html', template_dict)


def simpletest(request, whichtest):
    if whichtest == 'deletecomments':
        form = CommentDeleteForm()
    elif whichtest == 'deletetopics':
        form = TopicDeleteForm()
    elif whichtest == 'newtopic':
        form = NewTopicForm()
    elif whichtest == 'mergecomments':
        form = MergeCommentForm()
    else:
        raise Http404
        


    template_dict = {'form' : form, 'action' : whichtest }
    template_dict.update(csrf(request))

    return render_to_response('simpletest.html', template_dict)
        
def mergecomments(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/reporterview")

    if request.user.is_anonymous():
        return HttpResponseRedirect("/authenticate")

    userprofile = UserProfile.objects.get(user=request.user)

    if not userprofile.is_reporter():
        # Needs to handle this case better
        return HttpResponseRedirect("/authenticate")

    # So, it's a reporter

    form = MergeCommentForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect("/reporterview")

    comments = form.cleaned_data['comments']
    parent = form.cleaned_data['parent']

    for comment in comments:
        # Transfer all relations from comment to parent
        # Preserve the old relations, in case we re-split the comments at some point
        for left_relation in CommentRelation.objects.filter(left_comment=comment):
            new_relation = CommentRelation(left_comment = parent, right_comment = left_relation.right_comment, relation_type = left_relation.relation_type)
            new_relation.save()

        for right_relation in CommentRelation.objects.filter(right_comment=comment):
            new_relation = CommentRelation(left_comment = right_relation.left_comment, right_comment = parent, relation_type = right_relation.relation_type)
            new_relation.save()

        comment.is_parent = False
        comment.save()


        
        
    parent.is_parent = True
    parent.save()
    return HttpResponseRedirect("/reporterview")


def deletetopics(request):
    
    if request.method != 'POST':
        return HttpResponseRedirect("/reporterview")

    if request.user.is_anonymous():
        return HttpResponseRedirect("/authenticate")

    userprofile = UserProfile.objects.get(user=request.user)

    if not userprofile.is_reporter():
        # Needs to handle this case better
        return HttpResponseRedirect("/authenticate")

    # So, it's a reporter

    form = TopicDeleteForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect("/reporterview")

    for topic in form.cleaned_data['topics']:
       # We don't want to actually delete the topic.
       topic.is_deleted = True
       topic.save()

    return HttpResponseRedirect("/reporterview")

def deletecomments(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/reporterview")

    if request.user.is_anonymous():
        return HttpResponseRedirect("/authenticate")

    userprofile = UserProfile.objects.get(user=request.user)

    if not userprofile.is_reporter():
        # Needs to handle this case better
        return HttpResponseRedirect("/authenticate")

    # So, it's a reporter

    form = CommentDeleteForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect("/reporterview")

    for comment in form.cleaned_data['comments']:
       # We don't want to actually delete the comment.
       comment.is_deleted = True
       comment.save()

    return HttpResponseRedirect("/reporterview")

def newtopic(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/reporterview")

    if request.user.is_anonymous():
        return HttpResponseRedirect("/authenticate")

    userprofile = UserProfile.objects.get(user=request.user)

    if not userprofile.is_reporter():
        # Needs to handle this case better
        return HttpResponseRedirect("/authenticate")

    # So, it's a reporter

    form = NewTopicForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect("/reporterview")

    title = form.cleaned_data['title']
    summary_text = form.cleaned_data['summary_text']
    source_comment = form.cleaned_data['source_comment']

    curators = [userprofile]
    
    summary = Summary.objects.get_or_create(text=summary_text)[0] # get_or_create returns (obj, is_new)
    summary.save()

    topic = Topic(title = title, slug = slugify(title), summary = summary, is_deleted = False)
    topic.save()
    topic.curators = curators
    if source_comment:
        topic.comments = [source_comment]
    topic.save()

    return HttpResponseRedirect("/reporterview")





def frontpage(request):
    """ Front page demo"""

    if request.method == 'POST':
        if request.user.is_anonymous():
            # This scenario should be handled more gracefully in JavaScript
            return HttpResponseRedirect("/authenticate")
        
        # If someone just submitted a comment, load the form
        form = CommentSubmitForm(request.POST)
        
        if form.is_valid():
            # Validate the form
            comment_type = form.cleaned_data['comment_type_str'] # look up comment by name
            userprofile = UserProfile.objects.get(user = request.user) # Assumes consistency between users, UserProfiles
            comment = Comment(text = form.cleaned_data['text'], user = userprofile)
            comment.comment_type = comment_type
            comment.save() # We have to save the comment object so it has a primary key, before we can link tags to it.

            topic = form.cleaned_data['topic']

            comment.topics = [Topic.objects.get(title=topic)] # See forms for simplification possibilities
            comment.save()
            form = CommentSubmitForm() # successfully submitted, give them a new form
    
    else: form = CommentSubmitForm() # Give them a new form if have either a valid submission, or no submission
    template_dict = {}

    topics = Topic.objects.filter(is_deleted=False)[:5] # Will want to filter, order in later versions

    template_dict['topics'] = topics
    template_dict['comment_form'] = form
    template_dict.update(csrf(request)) # Required for csrf system
    return render_to_response('frontpage.html', template_dict,context_instance=RequestContext(request))
   
def index(request):
    """Really basic default view."""
    template_dict = {}

    return render_to_response('index.html', template_dict)


def api_topic_comments(request, topic_slug_or_id, output_format="json", page=1):
    """Return a paginated list of comments for a particular topic. """
    # See http://docs.djangoproject.com/en/dev/topics/pagination/?from=olddocs#using-paginator-in-a-view 

    # TODO: Break this out into a setting somewhere?
    ITEMS_PER_PAGE = 5 # Show 5 items per page

    try:
        # Right now we only support json as an output format
        if output_format != 'json':
            raise UnknownOutputFormatException("Unknown output format '%s'" % \
                                              (output_format))

        # topic_slug_or_id can either be a slug or an id
        if topic_slug_or_id.isdigit():
            # It's all numbers, so treat it as an id
            topic = Topic.objects.get(pk=int(topic_slug_or_id))
        else:
            # It's a slug
            topic = Topic.objects.get(slug=topic_slug_or_id) 

        # Serialize the data
        # See http://docs.djangoproject.com/en/dev/topics/serialization/ 
        # TODO: It might make sense to implement natural keys in order
        # to pass through useful user data.
        # See http://docs.djangoproject.com/en/dev/topics/serialization/#natural-keys 
        comments = topic.comments.filter(is_deleted=False).filter(is_parent=True)    
        paginator = Paginator(comments, ITEMS_PER_PAGE)

        # Make sure page request is an int.  If not deliver the first page.
        try:
            page_num = int(page)
        except ValueError:
            page_num = 1

        # If page request (9999) is out of range, deliver last page of results.
        try:
            comments_page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            comments_page = paginator.page(paginator.num_pages)

        data = serializers.serialize('json', comments_page.object_list,
                                     fields=('comment_type', 'text', 'user'),
                                     use_natural_keys=True)

    except UnknownOutputFormatException:
        pass
        # TODO: Handle this exception
        # QUESTION: What is the best way to return errors in JSON?
    except ObjectDoesNotExist:
        pass
        # TODO: Handle this exception

    return HttpResponse(data, mimetype='application/json') 

def api_comment_concur(request, comment_id, output_format='json'):
    logger.debug("got here!")
    data = ()
    return HttpResponse("")
    #return HttpResponse(data, mimetype='application/json')
