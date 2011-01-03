import json
import datetime

from django.http import HttpResponseRedirect, HttpResponse, \
                        HttpResponseNotFound, Http404
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.db.models import Count, Sum, Max

from fbapi.facebook import *

from core.models import Topic,CommentType, Comment, Summary, CommentRelation, \
                   CommentResponse
from core.exceptions import UnknownOutputFormat, NonAjaxRequest, \
                                       MissingParameter, RecentlyResponded, \
                                       MethodUnsupported, InvalidTopic, \
                                       MaximumExceeded, UserOwnsItem, \
                                       NotUserQuestionReply
from core.forms import CommentSubmitForm, CommentDeleteForm, \
                                  TopicDeleteForm, NewTopicForm, \
                                  MergeCommentForm, NewSummaryForm, \
                                  CommentTopicForm
import core.utils
from core.utils import CountIfConcur
from users.models import UserProfile, User
from users.views import ajax_login_required 
from users.exceptions import UserNotAuthenticated, UserNotReporter
from tagger.models import Tag
from clipper.forms import UrlSubmitForm


logger = core.utils.get_logger()

def browse_topics(request):

    logger.info('core.views.browse_topics(request)')
    topics = Topic.objects.all()
    template_dict = {'topics': topics}

    return render_to_response('core-topic-browse.html', template_dict, \
                              context_instance=RequestContext(request))

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
               data['error_html'] = core.utils.build_readable_errors(form.errors)
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

    topic = Topic(title = title, slug = core.utils.slugify(title), summary = summary, is_deleted = False)
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
        logger.info("core.views.api_commentsubmission(request, output_format=\
            'json')")
        if request.method:
            form = CommentSubmitForm(request.REQUEST)
            if request.user.is_anonymous():

                logger.info("core.views.api_commentsubmission(request, output_format=\
                    'json'): user is anonymous")
                status = 401 # Unauthorized
                data['error'] = "You need to log in"
                data['field_errors'] = form.errors
                data['error_html'] = core.utils.build_readable_errors(form.errors)

            userprofile = UserProfile.objects.get(user=request.user)

            if not form.is_valid():
                # Raise exceptions
                
                logger.info("core.views.api_commentsubmission(request, output_format=\
                    'json'): form not valid, errors= %s", form.errors)
                status = 400 # Bad request
                data['error'] = "Some required fields are missing or invalid."
                data['field_errors'] = form.errors
                data['error_html'] = core.utils.build_readable_errors(form.errors)


            else:
                # Form is good
                
                f_comment_type = form.cleaned_data['comment_type_str'] # a comment type
                f_text = form.cleaned_data['text'] # Text
                f_sources = form.cleaned_data['sources']
                f_topic = form.cleaned_data['topic']
                logger.info("core.views.api_commentsubmission(request, output_format=\
                    'json'): form is good, topic=%s, comment=%s, \
                    comment_type=%s", f_topic, f_text, f_comment_type)
                try: f_topic = Topic.objects.get(title = f_topic) # a topic name
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
                data = comment.id

                if f_in_reply_to: # Comment is in reply to another comment
                    reply_relation = CommentRelation(left_comment = comment, \
                        right_comment = f_in_reply_to, relation_type = 'reply')
                    reply_relation.save()


        else: # Not a post
            
            logger.info("core.views.api_commentsubmission(request, output_format=\
                'json'): not a post")
            raise MethodUnsupported("This endpoint only accepts POSTs, you used:" + request.method)
        
    except InvalidTopic:

        logger.info("core.views.api_commentsubmission(request, output_format=\
            'json'): Invalid topic")
        status = 400 # Bad Request
        data['error'] = "Invalid topic"

    logger.info("core.views.api_commentsubmission(request, output_format=\
        'json'): returning data=%s", data)
    return HttpResponse(content = json.dumps(data), mimetype='text/html', status=status)


def frontpage_q_filter(this_questions):
    if len(this_questions.topics.all()) > 0:
        return True
    else: return False

def frontpage_questions(count=10):
    """Return a list of questions to be displayed on the front page.

    Currently it returns the most recent questions in reverse chronological
    order.

    Keyword arguments:
    count -- Number fo questions to return (default 10)


    """
    questions = Comment.objects.filter(is_deleted=False, \
            comment_type__name="Question").order_by('-date_created')[:count]
    #issue 112, we have to make sure that questions w/o topics 
    #aren't allowed into the front page
    
    f_questions = filter(frontpage_q_filter, questions)
    return f_questions

def frontpage(request):
    """Front page view."""

    questions = frontpage_questions()

    logger.debug(questions)
    template_dict = { 'site_name': settings.SITE_NAME, \
        'body_classes': settings.SITE_BODY_CLASSES, \
        'questions': questions,
        'qa_form': CommentSubmitForm()}
    
    return render_to_response('frontpage.html', template_dict, \
        context_instance=RequestContext(request))
        
def signup(request):
    template_dict = { 'site_name': settings.SITE_NAME, \
        'body_classes': settings.SITE_BODY_CLASSES + " signup" }
    
    return render_to_response('signup.html', template_dict, \
        context_instance=RequestContext(request))
        
def topic(request, whichtopic=1):
    """ Display a topic page for a given topic. """

    clipper_url_form = UrlSubmitForm()

    # Determine if there is an authenticated user and get a little information
    # about that user.
    if not request.user.is_anonymous():
        # Logged in user
        # Assumes consistency between users, UserProfiles
        userprofile = UserProfile.objects.get(user = request.user) 

        is_reporter = userprofile.is_reporter()
    else:
        is_reporter = False
    
    if request.method == 'POST':
        if request.user.is_anonymous():
            # This scenario should be handled more gracefully in JavaScript
            return HttpResponseRedirect("/authenticate")
        
        # If someone just submitted a comment, load the form
        form = CommentSubmitForm(request.POST)
        
        if form.is_valid():
            # Validate the form

            # look up comment by name
            comment_type = form.cleaned_data['comment_type_str'] 


            comment = Comment(text = form.cleaned_data['text'], \
                              user = userprofile)
            comment.comment_type = comment_type
            # We have to save the comment object so it has a primary key, 
            # before we can link tags to it.
            comment.save() 

            topic = form.cleaned_data['topic']
            in_reply_to = form.cleaned_data['in_reply_to']
            
            # See forms for simplification possibilities
            comment.topics = [Topic.objects.get(title=topic)] 
            if form.cleaned_data['sources']:
                comment.sources = [form.cleaned_data['sources']]
            comment.save()
            # successfully submitted, give them a new form
            form = CommentSubmitForm() 

            if in_reply_to: # Comment is in reply to another comment
                reply_relation = CommentRelation(left_comment = comment, \
                                                 right_comment = in_reply_to, \
                                                 relation_type = 'reply')
                reply_relation.save()

    else: 
        # Give them a new form if have either a valid submission, or no 
        # submission
        form = CommentSubmitForm() 

    
    if Comment.objects.count() > 0:
        reply_form = CommentSubmitForm(initial = { \
            'in_reply_to' : Comment.objects.all()[0]})
    else:
        reply_form = None

    template_dict = { 'site_name':settings.SITE_NAME, \
        'body_classes':settings.SITE_BODY_CLASSES }

    # Will want to filter, order in later versions
    topics = Topic.objects.filter(is_deleted=False)[:5] 

    template_dict['topics'] = topics
    try: 
        topic =  Topic.objects.get(id=whichtopic)
        template_dict['topic'] = topic 
        template_dict['comments_to_show'] = topic.comments_to_show()
       
        # - Geoff Hing <geoffhing@gmail.com> 2010-12-02
        # Get a list of comment ids of comments that a user has voted on. 
        if request.user.is_anonymous():
            template_dict['user_voted_comment_ids'] = None
        else:
            template_dict['user_voted_comment_ids'] = \
                topic.user_voted_comment_ids(user_profile)

    except: 
        # No topic loaded
        pass

    template_dict['comment_form'] = form
    template_dict['reply_form'] = reply_form
    template_dict['comments'] = {}
    template_dict['clipper_url_form'] = clipper_url_form
    template_dict['fb_app_id']=settings.FB_API_ID
    template_dict['is_reporter'] = is_reporter
        
    template_dict.update(csrf(request)) # Required for csrf system

    return render_to_response('core-topic.html', template_dict, \
                              context_instance=RequestContext(request))
   
def index(request):
    """Really basic default view."""
    template_dict = {}

    return render_to_response('index.html', template_dict)


def topic_from_slug_or_id(topic_slug_or_id):
    # topic_slug_or_id can either be a slug or an id
    if topic_slug_or_id.isdigit():
        # It's all numbers, so treat it as an id
        topic = Topic.objects.get(pk=int(topic_slug_or_id))
    else:
        # It's a slug
        topic = Topic.objects.get(slug=topic_slug_or_id) 

    return topic


@ajax_login_required
def api_topic_delete(request, topic_slug_or_id=None, output_format="json"):
    data = {} # Data we'll eventually return as JSON
    status = 200 # HTTP response status.  Be optimistic
    response = None

    try:
        topic = topic_from_slug_or_id(topic_slug_or_id) 
        topic.is_deleted = True
        topic.save()

    except ObjectDoesNotExist:
        status = 404
        data['error'] = "Topic with slug or id %s does not exist" % \
            (topic_slug_or_id)

    response = HttpResponse(content=json.dumps(data), \
        mimetype='application/json', status=status)

    return response

@ajax_login_required
def api_topic(request, topic_slug_or_id=None, output_format="json"):
    data = {} # Data we'll eventually return as JSON
    status = 200 # HTTP response status.  Be optimistic
    response = None

    try:
        if request.method == 'DELETE':
            response = api_topic_delete(request, topic_slug_or_id, output_format) 
        else:
            raise MethodUnsupported("%s method is not supported at this time." %\
                request.method)

    except MethodUnsupported, e:
        status = 405 
        data['error'] = "%s" % e
        response = HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)
        
    return response

@ajax_login_required
def api_comment_tag(request, output_format="json"):
    data = {}
    status = 200
    response = None

    try:
        if request.method == 'POST':
            tagname = request.POST['tags']

            comment = Comment.objects.get(id=request.POST['comment'])

            if tagname.startswith("_"):
                tagname = tagname.replace("_", "_" + request.user.username +'_')
            tag = Tag.objects.get_or_create(name=tagname)[0]

            tag.save()

            comment.tags.add(tag)

            comment.save()

            data = {'tags' : [tag.name for tag in comment.tags.all()] }


        else:
            raise MethodUnsupported("%s method is not supported at this time." % request.method)


    except MethodUnsupported, e:
        status = 405
        data['error'] = "%s" % e

    except ObjectDoesNotExist:
        status = 404
        data['error'] = 'Cmment does not exist'

    response = HttpResponse(content=json.dumps(data), \
        mimetype='application/json', status=status)

    return response

@ajax_login_required
def api_topic_tag(request, output_format="json"):
    data = {}
    status = 200
    response = None

    try:
        if request.method == 'POST':
            tagname = request.POST['tags']

            topic = Topic.objects.get(id=request.POST['topic'])

            if tagname.startswith("_"):
                tagname = tagname.replace("_", "_" + request.user.username +'_')
            tag = Tag.objects.get_or_create(name=tagname)[0]

            tag.save()

            topic.topic_tags.add(tag)

            topic.save()

            data['tags'] = [tag.name for tag in topic.topic_tags.all()]


        else:
            raise MethodUnsupported("%s method is not supported at this time." % request.method)


    except MethodUnsupported, e:
        status = 405
        data['error'] = "%s" % e

    except ObjectDoesNotExist:
        status = 404
        data['error'] = "Topic does not exist"
            

    response = HttpResponse(content=json.dumps(data), \
        mimetype='application/json', status=status)

    return response
        


def generate_bootstrapper(request, question_id):
    """
    This method simply returns a test page to see
    what an implementing client would look like if they
    integrated a contribution list function into their site
    """
    template_dict = {}
    template_dict['rooturl'] = settings.SITE_URL
    template_dict['mediaurl'] = settings.MEDIA_URL
    template_dict['qid'] = question_id
    try:
        if request.method == 'GET':
            thiscomment = Comment.objects.get(id=question_id)
            topics = thiscomment.topics.all()
            #TODO: whats up in the event no topic exists?
            if len(topics) > 0:
                template_dict['topic_id'] = topics[0].id
            template_dict['question'] = thiscomment.text
            template_dict['quizzer'] = thiscomment.user.user.username
            users = {}
            answers = thiscomment.get_answers()
            for item in answers:
                users[item.user.user.username] = item.user.user.username
            users_string = ''
            #and another loop to make this list readable
            values = users.values()
            val_len = len(values) - 1
            for i, val in enumerate(values):
                if i != val_len:
                    users_string += val + ", "
                else:
                    users_string += val
            #for k,v in users.items():
            #    users_string += v + ", "
            template_dict['user_list'] = users_string
                
        else:
            raise MethodUnsupported("%s method is not supported at this time." %\
                request.method)

    except ObjectDoesNotExist:
        status = 404
        template_dict['error'] = "Comment with id %s does not exist" % \
            (topic_slug_or_id)

    return render_to_response('bootstrapper.js', template_dict)

@ajax_login_required
def api_topic_summary(request, topic_slug_or_id=None, output_format="json"):
    data = {} # Data we'll eventually return as JSON
    status = 200 # HTTP response status.  Be optimistic
    response = None

    try:
        if request.method == 'POST':
            new_summary_text = request.POST['summary']
            topic = topic_from_slug_or_id(topic_slug_or_id) 
            new_summary = Summary.objects.get_or_create(text=new_summary_text)[0]
            new_summary.save()
            topic.summary = new_summary 
            topic.save()

        else:
            raise MethodUnsupported("%s method is not supported at this time." %\
                request.method)

    except ObjectDoesNotExist:
        status = 404
        data['error'] = "Topic with slug or id %s does not exist" % \
            (topic_slug_or_id)

    except MethodUnsupported, e:
        status = 405 
        data['error'] = "%s" % e

    response = HttpResponse(content=json.dumps(data), \
        mimetype='application/json', status=status)

    return response


def api_topics(request, output_format="json"):
    """Return a JSON formatted list of topics. 
    
    Formats: json

    HTTP Method: GET

    Requires authentication: false

    Parameters:

    * result_type: Optional. Specifies what type of topics to be returned. 

        Valid values include:

        * all: Current default. All topics. 

        * popular: Topics are returned in descending order
                   based on the total number of positive "votes" for
                   the topics questions.

        * active: Topics are returned in descending order based on when
                  the last question was asked.

    * count: Optional.  Specifies the number of questions to be returned.  
             If not specified, all topics are returned.

    """
    
    try:
        if output_format != 'json':
            raise UnknownOutputFormat("Unknown output format '%s'" % \
                                              (output_format))

        # Get the type of result
        if 'result_type' in request.GET.keys():
            result_type = request.GET['result_type']
        else:
            result_type = 'all'
        logger.info('core.views.api_topics(request, output_format=\"json\"): \
            result_type = %s', result_type)
        if result_type == 'popular':
            topics = Topic.objects.filter(is_deleted=False).annotate(
                num_votes=CountIfConcur('comments__responses')).order_by(
                    '-num_votes')

        elif result_type == 'active':
            topics = Topic.objects.filter(is_deleted=False).annotate(
                latest_comment=Max('comments__date_created')).order_by(
                    '-latest_comment')
                    
        else:
            topics = Topic.objects.filter(is_deleted=False)

        # Get the number of questions to return
        if 'count' in request.GET.keys():
            count = int(request.GET['count'])
            limited_topics = topics[:count]

            logger.info('core.views.api_topics(request, output_format=\"json\"): \
                count = %s', count)
        else:
            limited_topics = topics 


        data = serializers.serialize('json', limited_topics,
                                     fields=('id', 'title', 'slug','summary'),
                                     use_natural_keys=True)

    except UnknownOutputFormat, e:
        logger.info('core.views.api_topics(request, output_format=\"json\"): \
            error = %s', e)
        pass
        # TODO: Handle this exception
        # QUESTION: What is the best way to return errors in JSON?
    except ObjectDoesNotExist, e:
        logger.info('core.views.api_topics(request, output_format=\"json\"): \
            error = %s', e)
        pass
        # TODO: Handle this exception


    logger.info('core.views.api_topics(request, output_format=\"json\"): \
        returning data')

    return HttpResponse(data, mimetype='application/json') 
        
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

        topic = topic_from_slug_or_id(topic_slug_or_id) 

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
        
                # Check accept case

                if response_type == 'accept':
                    # This should only be allowed for replies to comments posed by the user

                    # Is the comment a reply at all?
                    try: 
                        reply_relation = CommentRelation.objects.filter(left_comment = comment, relation_type = 'reply')
                    except ObjectDoesNotExist:
                        raise NotUserQuestionReply ("This is not a reply to a question")

                    # It's a reply, but who posed the initial question?

                    if not reply_relation.right_comment.user == user:
                        raise NotUserQuestionReply ("This is a reply to a question posed by another user; user cannot accept it")

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
    except NotUserQuestionReply, e:
        status = 403 # Forbidden
        data['error'] = "%s" % e

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)

def api_questions(request, output_format='json'):
    """Return a JSON formatted list of questions.
    
    Formats: json

    HTTP Method: GET

    Requires authentication: false

    Parameters:

    * result_type: Optional. Specifies what type of questions to be returned. 

        Valid values include:

        * popular: Current default.  Questions that have received the most 
                   positive "votes."  Questions are returned in descending order
                   of positive "votes" then by descending order of created date.

    * count: Optional.  Specifies the number of questions to be returned.  
             Defaults to 5

    """

    status = 200 # HTTP return status.  We'll be optimistic.
   
    try:
        if request.method == 'GET':
            # Get the number of questions to return
            if 'count' in request.GET.keys():
                count = int(request.GET['count'])
            else:
                count = 5 # Default to 5
            questions = Comment.objects.filter(is_deleted=False, \
                            comment_type__name="Question").annotate(\
                                num_responses=CountIfConcur('responses')).order_by(\
                                    '-num_responses', '-date_created')[:count]

            f_questions = filter(frontpage_q_filter, questions)
            content = serializers.serialize('json', f_questions, \
                                            fields=('text', 'topics'), \
                                            use_natural_keys=True)

        else:
            raise MethodUnsupported("%s is not supported at this time." % \
                                (request.method))

    except MethodUnsupported, e:
        status = 405 # Method not allowed
        data = {} # response data 
        data['error'] = "%s" % e
        content=json.dumps(data)

    return HttpResponse(content=content, mimetype='application/json', \
                        status=status)
