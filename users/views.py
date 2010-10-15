from models import UserProfile
from models import User

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from fbapi.facebook import *
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout



def do_login(username,password,request):

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

    The password becomes the facebook id, b/c no one should ever have to enter it 
    and the authenication on for our django site is a formality since facebook verified the user

    NOTE: The login page, when the user clicks the sign in via FB button a JS callback
    function is called and on successful logins it routes the browser to /authenticate
    to run necessary checks

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
        try:
            ouruser =  UserProfile.objects.get(facebook_user_id=user['uid'])
            #we need to log the FB user in
            #http://zcentric.com/2010/05/12/django-fix-for-user-object-has-no-attribute-backend/
            ouruser.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request,ouruser.user)
            return HttpResponseRedirect('/')
        except UserProfile.DoesNotExist:
            #they're not, so we need to create them and move em along
            graph = GraphAPI(user['access_token'])
            profile = graph.get_object("me")
            username=profile['first_name']+profile['last_name']
            password=profile['id']
            baseuser = User.objects.create_user(username=username,password=password,email='na')
            newuser = UserProfile(user=baseuser,facebook_user_id=profile['id'])
            newuser.save()
            return do_login(username,password,request)
    else:
       #no residual auth tokens found, move the user to login 
       return HttpResponseRedirect('login')


def weblogout(request):
    """
    log a django user out
    """
    logout(request)
    return HttpResponseRedirect('/')


def weblogin(request):
    """
    on the login page we can accept django username/password or they can use the facebook login button
         if the user enters django credentials, we try to log them in in the** doLogin(username,password,request)**
         if the user hits the facebook login button, they move through facebooks authentication flow and end up back on the page

     we have to check for the facebook cookie as we did in **auth(request)** and move them on (it should exist this time)

    """

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
        print 'trying to sign in'
        return do_login(fUsername, fPass, request)


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
            return do_login(fUsername,fPass,request)
