from models import UserProfile
from models import User
from forms import LoginForm, RegisterForm  
from fbapi.facebook import *
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from core.exceptions import MethodUnsupported, NonAjaxRequest
from users.exceptions import BadUsernameOrPassword, UserAccountDisabled

def disabled_act(request):
    template_dict = {}
    return render_to_response('disabled_user.html',\
        template_dict,context_instance=RequestContext(request))

def do_login(username,password,request):
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/disabled_act')
    else:
        #invalid login credentials / account doesn't exist
        #see forms.LoginForm.clean(self), we do the validation
        #there because it appears to be less of duplication of code
        #as well as using existing solutions to output error messages
        pass


def auth(request):
    """
    Facebook auth uses the Javascript SDK to authenticate in the browswer
    and it stocks a cookie

    The cookie is read on the server side in the **auth(request)** method
    * if that cookie exists and a django user doesn't, we create a django
     user and move them to the site
    **I set the username to be the first+last name to avoid spaces

    The password becomes the facebook id, b/c no one should ever have to
     enter it and the authenication on for our django site is a formality 
     since facebook verified the user

    NOTE: The login page, when the user clicks the sign in via FB button a
     JS callbacr function is called and on successful logins it routes the
     browser to /authenticate to run necessary checks

    if that cookie exists and a django user does, we move them to the site
    if no cookie exists, we move them onto the login page
    
    NOTE: if a user has a django account there is no method for them to add
     a facebook account if they decide to log in VIA facebook their prior 
     account won't be merged, thus we have two unique accounts with no
     bridge.  
    """
    if request.user.is_authenticated():    
        return HttpResponseRedirect('/')
    user = get_user_from_cookie(request.COOKIES, settings.FB_API_ID,\
        settings.FB_SECRET_KEY )
    if user:
        #user has a FB account and we need to see if they have been 
        #registered in our db
        try:
            ouruser =  UserProfile.objects.get(facebook_user_id=user['uid'])
            #we need to log the FB user in
            #http://zcentric.com/2010/05/12/django-fix-for-user-object-has-no-attribute-backend/
            #TODO: send message telling the user they have been logged in
            # via FB
            ouruser.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request,ouruser.user)
            return HttpResponseRedirect('/')
        except UserProfile.DoesNotExist:
            #they're not, so we need to create them and move em along
            graph = GraphAPI(user['access_token'])
            profile = graph.get_object("me")
            username=profile['first_name']+profile['last_name']
            password=profile['id']
            baseuser = User.objects.create_user(username=username,\
                password=password,email='na')
            newuser = UserProfile(user=baseuser,\
                facebook_user_id=profile['id'])
            newuser.save()
            return do_login(username,password,request)
    else:
       #no residual auth tokens found, move the user to login 
       return HttpResponseRedirect('login')


def weblogout(request):
    """
    log a django user out... if they
    logged in with Facebook we only 
    deauthorize their django user so when
    they return, if their fb cookie didn't
    expire then they will be logged back in
    w/o going to the login page (auth will
    catch them)
    """
    logout(request)
    return HttpResponseRedirect('/')


def weblogin(request):
    """
    on the login page we can accept django username/password or they can use
     the facebook login button
         if the user enters django credentials, we check those in do_login 
         if the user hits the facebook login button, they move through 
            we use Facebooks external authorization flow (which we verify in
            the auth method)
    """

    template_dict = {}
    template_dict['fb_app_id']=settings.FB_API_ID
    template_dict['auth_page']='authenticate'
    fbuser = get_user_from_cookie(request.COOKIES, settings.FB_API_ID,\
        settings.FB_SECRET_KEY )
    if fbuser:
        #the user hit this page again after using the FB signin link, 
        #move em to auth
        return HttpResponseRedirect('auth')
    if request.method == 'POST':
        #the user has submitted the form 
        form = LoginForm(request.POST)
        if form.is_valid():
            #things look good, log the user in
            fUsername = form.cleaned_data['username']
            fPass = form.cleaned_data['password']
            return do_login(fUsername, fPass, request)
        else:
            #user done messed up, let em know
            template_dict['form'] = form
            return render_to_response('login.html',template_dict,\
                context_instance=RequestContext(request))
    else:
        #the user is either coming to the login page from another page
        #or they had some issues submitting input correctly
        form = LoginForm()
        template_dict['form'] = form
    return render_to_response('login.html',template_dict,\
        context_instance=RequestContext(request))


def register(request):
    """
    The user has chosen not to auth through facebook and doesn't already 
    have django credentials
    """
    template_dict = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        template_dict['form'] = form
        if form.is_valid():
            #grab input
            f_username = form.cleaned_data['username']
            f_password = form.cleaned_data['password']
            f_email = form.cleaned_data['email']
            f_first_name = form.cleaned_data['first_name']
            f_last_name = form.cleaned_data['last_name']
            f_street_address = form.cleaned_data['street_address']
            f_city = form.cleaned_data['city']
            f_state = form.cleaned_data['state']
            f_zip_code = form.cleaned_data['zip_code']
            f_phone = form.cleaned_data['phone']
            f_dob = form.cleaned_data['dob']
            #we validate the username / email is unique by overriding
            #clean_field methods in RegisterForm
            baseuser = User.objects.create_user(username=f_username,\
                password=f_password, email=f_email)
            baseuser.first_name=f_first_name
            baseuser.last_name=f_last_name
            baseuser.save()
            newuser = UserProfile(user=baseuser, city=f_city,\
                street_address=f_street_address, state=f_state, zip=f_zip_code,\
                phone_number=f_phone)
            newuser.save()
            return do_login(f_username,f_password,request)
        else:
            return render_to_response('register.html', template_dict,\
                context_instance=RequestContext(request))
    if request.method != 'POST': 
        #get a new form
        form = RegisterForm()
        template_dict['form'] = form
        return render_to_response('register.html', template_dict,\
            context_instance=RequestContext(request))

def api_register(request):
    """Like register() but through AJAX"""
    pass

def api_auth(request):
    """Like auth() but through AJAX"""

    data = {} # Response data 
    status = 200 # Ok

    try:
        if request.is_ajax():
            if request.method == 'POST':
                form = LoginForm(request.POST)

                if form.is_valid():
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password']

                    # Try to authenticate the user
                    user = authenticate(username=username, password=password)

                    if user is not None:
                        if user.is_active:
                            login(request, user)
                        else:
                            raise UserAccountDisabled
                    else:
                        raise BadUsernameOrPassword

                else:
                    # user done messed up, let em know
                    status = 400 # Bad Request
                    data['error'] = "Some required fields are missing"
                    data['field_errors'] = form.errors

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

    except BadUsernameOrPassword, error:
        status = 401 # Unauthorized
        data['error'] = "%s" % error

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)

def api_users(request):
    """Catch-all view for user api calls."""
    pass
