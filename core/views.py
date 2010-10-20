from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator
from fbapi.facebook import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from radregator.users.models import UserProfile,User
from django.contrib.auth import authenticate, login, logout

from models import Topic,CommentType, Comment, Summary, CommentRelation, CommentResponse
from radregator.tagger.models import Tag
from radregator.core.forms import CommentSubmitForm, CommentDeleteForm, TopicDeleteForm, NewTopicForm, MergeCommentForm
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from radregator.core.commentdeleteform' : CommentDeleteForm(),
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



def replytocomment(request):
    if request.method == 'POST':
        if request.user.is_anonymous():
            return HttpResponseReirect("/authenticate")

        form = CommentReplyForm(request.POST)

        if not form.is_valid():
            # Raise exceptions
            return HttpResponseRedirect("/frontpage")
            

    return HttpResponseRedirect("/frontpage")


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
       Request data: {"type":"concur"}
       Response code: 201 Created
       Response data: {"uri": "/api/json/comments/1/responses/1/"} 
       
    """

    # A user can only respond once during this time period
    RESPONSE_WINDOW_HOURS = 0
    RESPONSE_WINDOW_MINUTES = 5

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

                if "type" not in request_data.keys():
                    raise MissingParameter("You must specify a 'type' parameter to indicate which kind of comment response is being created")

                # Try to get the comment object
                comment = Comment.objects.get(id = comment_id)

                try:
                    # Check if the user has already responded
                    response = CommentResponse.objects.get(comment=comment, \
                        user__user__id=user_id,type=request_data['type'])

                except ObjectDoesNotExist:
                    pass
                    # The user hasn't responded to this comment.  We're cool.
                else:
                    # Get the current time
                    now = datetime.datetime.now()

                    # Get the difference between now and when the user last 
                    # responded
                    time_diff = now - response.created

                    # Calculate the allowable window
                    time_window = datetime.timedelta( \
                        hours=RESPONSE_WINDOW_HOURS, \
                        minutes=RESPONSE_WINDOW_MINUTES);

                    # Check when the user commented
                    if time_diff < time_window:
                      # User has already commented within the allowable window 

                      # Calculate how long the user has to wait
                      wait = time_window - time_diff
                      wait_hours, remainder = divmod(wait.seconds, 3600)
                      wait_minutes, wait_seconds = divmod(remainder, 60)

                      raise RecentlyResponded( \
                        "You must wait %d hours, %d minutes before responding" % \
                        (wait_hours, wait_minutes))
        
                comment_response = CommentResponse(user=user, comment=comment, \
                                                   type=request_data['type']) 
                comment_response.save()

                status = 201
                data['uri'] = "/api/%s/comments/%s/responses/%s/" % \
                              (output_format, comment_id, comment_response.id)
                    
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

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)
