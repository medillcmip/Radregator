from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator
from fbapi.facebook import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from radregator.users.models import UserProfile,User
from django.contrib.auth import authenticate, login, logout

from models import Topic, CommentType, Comment, CommentResponse
from radregator.tagger.models import Tag
from radregator.core.forms import CommentSubmitForm
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from radregator.core.exceptions import UnknownOutputFormat 
from django.core import serializers

import logging
import json

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

    topics = Topic.objects.all()[:5] # Will want to filter, order in later versions

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
            raise UnknownOutputFormat("Unknown output format '%s'" % \
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
        comments = topic.comments.all()    
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

    except UnknownOutputFormat:
        pass
        # TODO: Handle this exception
        # QUESTION: What is the best way to return errors in JSON?
    except ObjectDoesNotExist:
        pass
        # TODO: Handle this exception

    return HttpResponse(data, mimetype='application/json') 

def api_comment_responses(request, comment_id, output_format='json',
                          response_id=None):
    """Provide RESTful responses to calls for comment responses.
    
       Example API calls:
       
       Create a new concur response
       Method: POST
       URI: /api/json/comments/1/responses/
       Request data: {"type":"concur"}
       Response code: 201 Created
       Response data: {"uri": "/api/json/comments/1/responses/1/"} 
       
    """

    data = {}
    status=200 # Be optimistic

    try:
        if request.is_ajax():
            user_id = request.session.get('_auth_user_id', False)

            if user_id: 
                # User is logged in, get the user object
                user = UserProfile.objects.get(user__id = user_id)
            else:
                pass
                # TODO: Handle the case when a user who isn't logged in tries
                # to comment.

            if request.method == 'POST':
                request_data = json.loads(request.raw_post_data)

                # TODO validate request_data

                # Try to get the comment object
                comment = Comment.objects.get(id = comment_id)

                # TODO: Check if user has already responded

                comment_response = CommentResponse(user=user, comment=comment, \
                                                   type=request_data['type']) 
                comment_response.save()

                status = 201
                data['uri'] = "/api/%s/comments/%s/responses/%s/" % \
                              (output_format, comment_id, comment_response.id)
                    
            elif request.method == 'PUT':
                pass
            elif request.method == 'DELETE':
                pass
            else:
                # GET 
                pass
        else:
            # Non-AJAX request.  Disallow for now.
            raise NonAjaxRequest("Remote API calls aren't allowed right now.  This might change some day.")

    except ObjectDoesNotExist:
        # TODO: Handle this exception
        pass
    except NonAjaxRequest, e:
        status = 403 # Forbidden
        data['error'] = e

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)
