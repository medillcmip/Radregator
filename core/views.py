from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.paginator import Paginator
from fbapi.facebook import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from radregator.users.models import UserProfile,User
from django.contrib.auth import authenticate, login, logout

from models import Topic,CommentType, Comment
from radregator.tagger.models import Tag
from radregator.core.forms import CommentSubmitForm
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from radregator.core.exceptions import UnknownOutputFormatException 
from django.core import serializers

def frontpage(request):
    """ Front page demo"""

    if request.method == 'POST':
        
        # If someone just submitted a comment, load the form
        form = CommentSubmitForm(request.POST)
        
        if form.is_valid():
            # Validate the form
            comment_type = CommentType.objects.get(name=form.cleaned_data['comment_type_str']) # look up comment by name
            userprofile = UserProfile.objects.get(user = request.user) # Needs to handle failure, display error message
            comment = Comment(text = form.cleaned_data['text'], user = userprofile)
            comment.comment_type = comment_type
            comment.save() # We have to save the comment object so it has a primary key, before we can link tags to it.

            topic = form.cleaned_data['topic']
            comment.tags = form.cleaned_data['tags']
            if form.cleaned_data['newtag']:
                newtag = Tag.objects.get_or_create(name=form.cleaned_data['newtag'])[0] 
                # The [0] is because we get in indication if it's a new tag; we don't care, tho
                newtag.save()
                comment.tags.add(newtag)

            comment.topics = [Topic.objects.get(title=topic)] # See forms for simplification possibilities
            comment.save()
            form = CommentSubmitForm() # successfully submitted, give them a new form
    
    else: form = CommentSubmitForm() # Give them a new form if have either a valid submission, or no submission
    template_dict = {}

    topics = Topic.objects.all()[:5] # Will want to filter, order in later versions

    template_dict['topics'] = topics
    template_dict['comment_form'] = form
    template_dict.update(csrf(request)) # Required for csrf system

    return render_to_response('frontpage.html', template_dict)
    
def index(request):
    """Really basic default view."""
    template_dict = {}

    return render_to_response('index.html', template_dict)


def doLogin(username,password,request):

    user = authenticate(username=username, password=password)
    
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/')
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
            pass
    else:
        # Return an 'invalid login' error message.
        pass

def auth(request):
    """
    Facebook auth uses the Javascript SDK to authenticate in the browswer and it stocks a cookie
    The cookie is read on the server side in the **auth(request)** method
    * if that cookie exists and a django user doesn't, we create a django user and move them to the site
    **I set the username to be the first+last name to avoid spaces
    The password becomes the facebook id, b/c no one should ever have to enter it and the authenication on for our django site is a formality since facebook verified the user
    if that cookie exists and a django user does, we move them to the site
    if no cookie exists, we move them onto the login page
    
    NOTE: if a user has a django account there is no method for them to add a facebook account
    if they decide to log in VIA facebook their prior account won't be merged, thus we 
    have two unique accounts with no bridge.  
    """
    if request.user.is_authenticated():    
        return HttpResponseRedirect('/')
    user = get_user_from_cookie(request.COOKIES, settings.FB_API_ID,settings.FB_SECRET_KEY )
    if user:
        #user has a FB account and we need to see if they have been registered in our db
        ouruser =  UserProfile.objects.filter(facebook_user_id=user['uid'])
        if ouruser:
            return HttpResponseRedirect('/')
        else:#they're not, so we need to create them and move em along
            graph = GraphAPI(user['access_token'])
            profile = graph.get_object("me")
            username=profile['first_name']+profile['last_name']
            password=profile['id']
            baseuser = User.objects.create_user(username=username,password=password,email='na')
            newuser = UserProfile(user=baseuser,facebook_user_id=profile['id'])
            newuser.save()
            return doLogin(username,password,request)
    else:
       #no residual auth tokens found, move the user to login 
       return HttpResponseRedirect('login')

def weblogin(request):
    """on the login page we can accept django username/password or they can use the facebook login button
         if the user enters django credentials, we try to log them in in the** doLogin(username,password,request)**
         if the user hits the facebook login button, they move through facebooks authentication flow and end up back on the page

     we have to check for the facebook cookie as we did in **auth(request)** and move them on (it should exist this time)"""

    template_dict = {}
    template_dict['fb_app_id']=settings.FB_API_ID
    template_dict['auth_page']='authenticate'
    fbuser = get_user_from_cookie(request.COOKIES, settings.FB_API_ID,settings.FB_SECRET_KEY )
    if fbuser:
        #the user hit this page again after using the FB signin link, move em to auth
        return HttpResponseRedirect('auth')
    if request.method != 'POST':
        #we want to render the login page for input
        return render_to_response('login.html',template_dict,context_instance=RequestContext(request))
    else:
        #the user choose our sign in and we need to validate
        fUsername = request.POST.get('fUsername','')
        fPass = request.POST.get('fPassword','')
        return doLogin(fUsername, fPass, request)


def register(request):
    """
    The user has chosen not to auth through facebook and doesn't already have django credentials
    we look for an existing user, if they exist TODO: need to throw them somewheres with a msg
    Otherwise, we grab the info from the form, create the user instance and forward them on to get authenicated
    """
    template_dict = {}
    if request.method != 'POST': 
        #need to render the page
        return render_to_response('register.html', template_dict,context_instance=RequestContext(request))
    else:
        #we will get the info, save the object, log the user in and authenticate him
        fUsername = request.POST.get('fUsername', '')
        fPass = request.POST.get('fPassword','')
        try:
            baseuser = User.objects.get(username=fUsername)
            #TODO: adding some form of propagating exceptions for field checks
            #we have a user w this username already, throw them back to register page
            #TODO: some notification of the issue
            return render_to_response('register.html', template_dict,context_instance=RequestContext(request))
        except User.DoesNotExist:
            #we're cool, proceed with creating a user
            baseuser = User.objects.create_user(username=fUsername,password=fPass,email='na') 
            newuser = UserProfile(user=baseuser)
            newuser.save()
            return doLogin(fUsername,fPass,request)

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
                                     fields=('comment_type', 'text', 'user'))

    except UnknownOutputFormatException:
        pass
        # TODO: Handle this exception
    except ObjectDoesNotExist:
        pass
        # TODO: Handle this exception

    return HttpResponse(data, mimetype='application/json') 
