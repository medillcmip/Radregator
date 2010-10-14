from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from fbapi.facebook import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from radregator.users import models
from django.contrib.auth import authenticate, login, logout

from models import Topic
from radregator.core.forms import CommentSubmitForm
from django.core.context_processors import csrf

def frontpage(request):
    """ Front page demo"""

    if request.method == 'POST':
        
        form = CommentSubmitForm(request.POST)
        if form.is_valid():
            comment = model.save(commit = False)
            comment.user = UserProfile.get(user=request.user)
            comment.topics += request.POST['topic']
            comment.save()
            comment.save_m2m()

    template_dict = {}

    topics = Topic.objects.all()[:5] # Will want to filter, order in later versions

    template_dict['topics'] = topics
    template_dict['comment_form'] = CommentSubmitForm()
    template_dict.update(csrf(request))

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
            return HttpResponseRedirect('index')
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
            pass
    else:
        # Return an 'invalid login' error message.
        pass

def auth(request):
    """Facebook auth uses the Javascript SDK to authenticate in the browswer and it stocks a cookie
    The cookie is read on the server side in the **auth(request)** method
    * if that cookie exists and a django user doesn't, we create a django user and move them to the site
    **I set the username to be the first+last name to avoid spaces
    The password becomes the facebook id, b/c no one should ever have to enter it and the authenication on for our django site is a formality since facebook verified the user
    if that cookie exists and a django user does, we move them to the site
    if no cookie exists, we move them onto the login page"""

    user = get_user_from_cookie(request.COOKIES, settings.FB_API_ID,settings.FB_SECRET_KEY )
    if user:
        #user has a FB account and we need to see if they have been registered in our db
        ouruser =  models.UserProfile.objects.filter(facebook_user_id=user['uid'])
        if ouruser:
            return HttpResponseRedirect('index')
        else:#they're not, so we need to create them and move em along
            graph = GraphAPI(user['access_token'])
            profile = graph.get_object("me")
            username=profile['first_name']+profile['last_name']
            password=profile['id']
            baseuser = models.User.objects.create_user(username=username,password=password,email='na')
            newuser = models.UserProfile(user=baseuser,facebook_user_id=profile['id'])
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
            baseuser = models.User.objects.get(username=fUsername)
            #TODO: adding some form of propagating exceptions for field checks
            #we have a user w this username already, throw them back to register page
            #TODO: some notification of the issue
            return render_to_response('register.html', template_dict,context_instance=RequestContext(request))
        except models.User.DoesNotExist:
            #we're cool, proceed with creating a user
            baseuser = models.User.objects.create_user(username=fUsername,password=fPass,email='na') 
            newuser = models.UserProfile(user=baseuser)
            newuser.save()
            return doLogin(fUsername,fPass,request)
