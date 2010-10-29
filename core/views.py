from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator
from radregator.fbapi.facebook import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from radregator.users.models import UserProfile,User
from django.contrib.auth import authenticate, login, logout

from radregator.core.models import Topic,CommentType, Comment, Summary, CommentRelation, \
                   CommentResponse
from radregator.tagger.models import Tag
from radregator.core.forms import CommentSubmitForm, CommentDeleteForm, \
                                  TopicDeleteForm, NewTopicForm, \
                                  MergeCommentForm, NewSummaryForm
from radregator.core.forms import CommentTopicForm
from radregator.clipper.forms import UrlSubmitForm
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from radregator.core.exceptions import UnknownOutputFormat, NonAjaxRequest, \
                                       MissingParameter, RecentlyResponded, \
                                       MethodUnsupported, InvalidTopic, \
                                       MaximumExceeded, UserOwnsItem
from radregator.users.exceptions import UserNotAuthenticated, UserNotReporter
from django.core import serializers
import radregator.core.utils
from django.http import Http404

import json
import datetime

def reporterview(request):
    """ VERY rudimentary reporter view"""

    template_dict = {
        'commentdeleteform' : CommentDeleteForm(),
        'topicdeleteform' : TopicDeleteForm(),
        'newtopicform' : NewTopicForm(),
        'newsummaryform' : NewSummaryForm(),
        'mergecommentform' : MergeCommentForm(),
        'associatecommentform' : CommentTopicForm(),
        'disassociatecommentform' : CommentTopicForm(),

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
    elif whichtest == 'newsummary':
        form = NewSummaryForm()
    elif whichtest == 'mergecomments':
        form = MergeCommentForm()
    elif whichtest == 'associatecomment':
        form = CommentTopicForm()
    elif whichtest == 'disassociatecomment':
        form = CommentTopicForm()
    elif whichtest == 'commentsubmit':
        form = CommentSubmitForm()
    else:
        raise Http404
        


    template_dict = {'form' : form, 'action' : whichtest }
    template_dict.update(csrf(request))

    return render_to_response('simpletest.html', template_dict)
        
def check_reporter(request):
    if request.user.is_anonymous():
        raise UserNotAuthenticated()

    userprofile = UserProfile.objects.get(user=request.user)

    if not userprofile.is_reporter():
        raise UserNotReporter()
    
    return userprofile

        
    
def reporter_api(request, formconstructor, logic):
    """ Handle reporter operations"""

    data = {} # response data
    status = 200 # OK

    try:
        if request.method == 'POST':
           userprofile = check_reporter(request) 

           form = formconstructor(request.POST)

           if not form.is_valid():
               status = 400 # Caught in a bad request
               data['error'] = "Some required fields are missing or invalid"
               data['field_errors'] = form.errors
           else:
               # Form is good 
               logic(form, userprofile)
        else:
            # Not a post
            raise MethodUnsupported("This endpoint only accepts POSTs, you used: " + request.method)

    except UserNotReporter:
        status = 403 # forbidden
        data['error'] = 'User must be reporter'
    except UserNotAuthenticated:
        status = 401 # unauthorized
        data['error'] = 'User not logged in'

    return HttpResponse(content = json.dumps(data), mimetype='application/json', status=status)

def login_status(request):
    data = {}
    status = 200

    try:
        check_reporter(request)
    except UserNotReporter:
        status = 403
        data['error']= 'User must be reporter'
    except UserNotAuthenticated:
        status = 401 # unauthorized
        data['error'] = 'User not logged in'

    return HttpResponse(content = json.dumps(data), mimetype='application/json', status=status)
    

def disassociatecomment_logic(form, userprofile):
   comment = form.cleaned_data['comment']
   topic = form.cleaned_data['topic']

   comment.topics.remove(topic)
   comment.save()
   topic.save()

def associatecomment_logic(form, userprofile):
    comment = form.cleaned_data['comment']
    topic = form.cleaned_data['topic']

    comment.topics.add(topic)
    comment.save()
    topic.save()

def mergecomment_logic(form, userprofile):
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

def disassociatecomment(request):
    return reporter_api(request, CommentTopicForm, disassociatecomment_logic)
    
def associatecomment(request):
    return reporter_api(request, CommentTopicForm, associatecomment_logic)

def mergecomments(request):
    return reporter_api(request, MergeCommentForm, mergecomment_logic)

def topicdelete_logic(form, userprofile):
    for topic in form.cleaned_data['topics']:
       # We don't want to actually delete the topic.
       topic.is_deleted = True
       topic.save()

def commentdelete_logic(form, userprofile):
    
    for comment in form.cleaned_data['comments']:
       # We don't want to actually delete the comment.
       print comment
       comment.is_deleted = True
       comment.save()

def deletetopics(request):
    return reporter_api(request, TopicDeleteForm, topicdelete_logic)
    
def deletecomments(request):
    return reporter_api(request, CommentDeleteForm, commentdelete_logic)

def newsummary_logic(form, userprofile):
    summary_text = form.cleaned_data['summary_text']
    topic = form.cleaned_data['topic'] # A topic object

    summary = Summary.objects.get_or_create(text=summary_text)[0] # get_or_create returns (obj, is_new)
    summary.save()

    topic.summary = summary
    topic.save()

    
def newtopic_logic(form, userprofile):
    title = form.cleaned_data['title']
    summary_text = form.cleaned_data['summary_text']
    source_comment = form.cleaned_data['source_comment']

    curators = [userprofile]
    
    summary = Summary.objects.get_or_create(text=summary_text)[0] # get_or_create returns (obj, is_new)
    summary.save()

    topic = Topic(title = title, slug = radregator.core.utils.slugify(title), summary = summary, is_deleted = False)
    topic.save()
    topic.curators = curators
    if source_comment:
        topic.comments = [source_comment]
    topic.save()

def newtopic(request):
    return reporter_api(request, NewTopicForm, newtopic_logic)

def newsummary(request):
    return reporter_api(request, NewSummaryForm, newsummary_logic)

def api_commentsubmission(request, output_format = 'json'):
    
    data = {} # response data
    status = 200 # OK

    try:
        if request.method:

            form = CommentSubmitForm(request.REQUEST)

            if request.user.is_anonymous():
                status = 401 # Unauthorized
                data['error'] = "You need to log in"
                data['field_errors'] = form.errors

            userprofile = UserProfile.objects.get(user=request.user)

            if not form.is_valid():
                # Raise exceptions

                status = 400 # Bad request
                data['error'] = "Some required fields are missing or invalid."
                data['field_errors'] = form.errors


            else:
                # Form is good
                
                f_comment_type = form.cleaned_data['comment_type_str'] # a comment type
                f_text = form.cleaned_data['text'] # Text
                f_sources = form.cleaned_data['sources']
                try: f_topic = Topic.objects.get(title = form.cleaned_data['topic']) # a topic name
                except:
                    raise InvalidTopic()

                f_in_reply_to = form.cleaned_data['in_reply_to'] # a comment

                comment = Comment(text = form.cleaned_data['text'], user = userprofile)
                comment.comment_type = f_comment_type
                comment.save()
                comment.topics = [f_topic]
                if f_sources:
                    comment.sources = [f_sources]
                comment.save()

                if f_in_reply_to: # Comment is in reply to another comment
                    reply_relation = CommentRelation(left_comment = comment, right_comment = f_in_reply_to, relation_type = 'reply')
                    reply_relation.save()


        else: # Not a post
            raise MethodUnsupported("This endpoint only accepts POSTs, you used:" + request.method)
        
    except InvalidTopic:
        status = 400 # Bad Request
        data['error'] = "Invalid topic"

    return HttpResponse(content = json.dumps(data), mimetype='text/html', status=status)
    # TK - need code on JavaScript side to to Ajax, etc.
    return HttpResponseRedirect("/")


            







    

def frontpage(request):
    """ Front page demo"""
    clipper_url_form = None
    
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
            in_reply_to = form.cleaned_data['in_reply_to']

            comment.topics = [Topic.objects.get(title=topic)] # See forms for simplification possibilities
            if form.cleaned_data['sources']:
                comment.sources = [form.cleaned_data['sources']]
            comment.save()
            form = CommentSubmitForm() # successfully submitted, give them a new form

            if in_reply_to: # Comment is in reply to another comment
                reply_relation = CommentRelation(left_comment = comment, right_comment = in_reply_to, relation_type = 'reply')
                reply_relation.save()

    
    else: 
        form = CommentSubmitForm() # Give them a new form if have either a valid submission, or no submission
        clipper_url_form = UrlSubmitForm()

    if not request.user.is_anonymous():
        # Logged in user
        is_reporter = UserProfile.objects.get(user = request.user).is_reporter()
    else:
        is_reporter = False
        
        
    reply_form = CommentSubmitForm(initial = {'in_reply_to' : Comment.objects.all()[0]})
    template_dict = {}

    topics = Topic.objects.filter(is_deleted=False)[:5] # Will want to filter, order in later versions

    template_dict['topics'] = topics
    template_dict['comment_form'] = form
    template_dict['reply_form'] = reply_form
    template_dict['comments'] = {}
    template_dict['clipper_url_form'] = clipper_url_form
    template_dict['is_reporter'] = is_reporter
    print is_reporter
        
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
       Request paramets:
        type:   "concur"
       Response code: 201 Created
       Response data: {"uri": "/api/json/comments/1/responses/1/"} 
       
    """

    # A user can only respond once during this time period
    # Set these to numbers to make limits take effect,
    # set to None for no limits
    #RESPONSE_WINDOW_HOURS = 0
    #RESPONSE_WINDOW_MINUTES = 5
    RESPONSE_WINDOW_HOURS = None 
    RESPONSE_WINDOW_MINUTES = None 

    # A user can only make this many responses per comment, per type
    MAX_RESPONSES = 1

    data = {}
    status=200 # Be optimistic

    try:
        if request.is_ajax():
            user_id = request.session.get('_auth_user_id', False)

            if user_id: 
                # User is logged in, get the user object
                user = UserProfile.objects.get(user__id = user_id)
            else:
                raise UserNotAuthenticated

            if request.method == 'POST':
                if "type" not in request.POST.keys():
                    raise MissingParameter("You must specify a 'type' " + \
                        "parameter ' + 'to indicate which kind of comment " + \
                        "response is being created")

                response_type = request.POST['type']

                # Try to get the comment object
                comment = Comment.objects.get(id = comment_id)

                # Check to see if the user created the comment.  You can't
                # respond to a comment you created.
                if comment.user.user.id == user.id:
                    # They match!
                    raise UserOwnsItem("You can't vote on an item that you " + \
                                       "created!")

                # Get any previous responses
                responses = CommentResponse.objects.filter(comment=comment, \
                    user__user__id=user_id, \
                    type=response_type).order_by('created')

                if responses.count() < MAX_RESPONSES and \
                   responses.count() > 0:
                    # User hasn't exceeded the maximum number of responses 
                    # allowed
                    
                    if RESPONSE_WINDOW_HOURS is not None and \
                       RESPONSE_WINDOW_MINUTS is not None:
                        # If time limits are enabled check to see
                        # if the user has commented too recently
                    
                        # Get the current time
                        now = datetime.datetime.now()

                        # Get the difference between now and when the user last 
                        # responded
                        time_diff = now - responses[0].created

                        # Calculate the allowable window
                        time_window = datetime.timedelta( \
                            hours=RESPONSE_WINDOW_HOURS, \
                            minutes=RESPONSE_WINDOW_MINUTES);

                        if time_diff < time_window:
                          # User has already commented within the allowable 
                          # window 

                          # Calculate how long the user has to wait
                          wait = time_window - time_diff
                          wait_hours, remainder = divmod(wait.seconds, 3600)
                          wait_minutes, wait_seconds = divmod(remainder, 60)

                          raise RecentlyResponded( \
                            "You must wait %d hours, %d minutes " +
                            "before responding" % (wait_hours, wait_minutes))

                elif responses.count() == 0:
                    pass
                            
                else:
                    raise MaximumExceeded("User has already made maximum " + \
                                          "number of responses")
        
                comment_response = CommentResponse(user=user, \
                                                   comment=comment, \
                                                   type=response_type) 
                comment_response.save()

                status = 201
                data['uri'] = "/api/%s/comments/%s/responses/%s/" % \
                              (output_format, comment_id, \
                               comment_response.id)
                    
            elif request.method == 'PUT':
                raise MethodUnsupported("PUT is not supported at this time.")

            elif request.method == 'DELETE':
                raise MethodUnsupported("DELETE is not supported at this time.")
                
            else:
                # GET 
                raise MethodUnsupported("GET is not supported at this time.")

        else:
            # Non-AJAX request.  Disallow for now.
            raise NonAjaxRequest( \
                "Remote API calls aren't allowed right now. " + \
                "This might change some day.")

    except ObjectDoesNotExist, e:
        status = 404 # Not found
        data['error'] = "%s" % e
    except NonAjaxRequest, e:
        status = 403 # Forbidden
        data['error'] = "%s" % e
    except MissingParameter, e:
        status = 400 # Bad Request
        data['error'] = "%s" % e
    except RecentlyResponded, e:
        status = 403 # Forbidden
        data['error'] = "%s" % e
    except MethodUnsupported, e:
        status = 405 # Method not allowed
        data['error'] = "%s" % e
    except UserNotAuthenticated as e:
        status = 401 # Unauthorized
        data['error'] = "%s" % e
    except MaximumExceeded as e:
        status = 403 # Forbidden
        data['error'] = "%s" % e
    except UserOwnsItem, e:
        status = 403 # Forbidden
        data['error'] = "%s" % e

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)
