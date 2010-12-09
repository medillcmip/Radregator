import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout

from fbapi import facebook 
from core.exceptions import MethodUnsupported, NonAjaxRequest
from users.exceptions import BadUsernameOrPassword, UserAccountDisabled, \
                             UserUsernameExists, UserEmailExists, \
                             NoFacebookUser
import core.utils

from models import UserProfile
from models import User
from forms import LoginForm, RegisterForm, InviteForm 

logger = core.utils.get_logger()

def ajax_login_required(view_func):
    """
    Decorator for AJAX endpoints requiring authentication.
    
    Thank you http://stackoverflow.com/questions/312925/django-authentication-and-ajax-urls-that-require-login/523196#523196
    
    """

    def wrap(request, *args, **kwargs):
        status = 200 
        data = {}

        try:
            if request.is_ajax():
                if request.user.is_authenticated():
                    return view_func(request, *args, **kwargs)

                else:
                    raise BadUsernameOrPassword

            else:
                # Non-AJAX request.  Disallow for now.
                raise NonAjaxRequest( \
                    "Remote API calls aren't allowed right now. " + \
                    "This might change some day.")

        except NonAjaxRequest, e:
            status = 403 # Forbidden
            data['error'] = "%s" % e
        except BadUsernameOrPassword, error:
            status = 401 # unauthorized
            data['error'] = "%s" % error

        return HttpResponse(content=json.dumps(data), \
            mimetype='application/json', status=status)

    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__

    return wrap


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

    # Check to see if there's a cookie indicating that the user
    # is logged in with Facebook.
    fb_user = facebook.get_user_from_cookie(request.COOKIES, \
                                            settings.FB_API_ID,\
                                            settings.FB_SECRET_KEY)

    if fb_user:
        #user has a FB account and we need to see if they have been 
        #registered in our db
        try:
            user_profile =  UserProfile.objects.get(\
                facebook_user_id=fb_user['uid'])
            #we need to log the FB user in
            #http://zcentric.com/2010/05/12/django-fix-for-user-object-has-no-attribute-backend/
            #TODO: send message telling the user they have been logged in
            # via FB
            user_profile.user.backend = \
                'django.contrib.auth.backends.ModelBackend'
            login(request, user_profile.user)

            return HttpResponseRedirect('/')

        except UserProfile.DoesNotExist:
            #they're not, so we need to create them and move em along
            fb_graph = facebook.GraphAPI(fb_user['access_token'])
            fb_profile = fb_graph.get_object("me")
            username = fb_profile['first_name'] + fb_profile['last_name']
            password = fb_profile['id']
            base_user = User.objects.create_user(username=username,\
                                                 password=password, email='na')
            new_user_profile = UserProfile(user=base_user,\
                                           facebook_user_id=fb_profile['id'])
            new_user_profile.save()

            return do_login(username, password, request)

    else:
       #no residual auth tokens found, move the user to login 
       return HttpResponseRedirect('login')


def weblogout(request):
    """
    log a django user out... 
    Facebook logout is handled via Javascript.
    """
    logout(request)
    return HttpResponseRedirect('/')


def api_login(request):
    """
    only need to return the page for the colorbox to display the page and
    the logic inside the login.html page takes care of the rest 
    """

    template_dict = {}
    template_dict['fb_app_id'] = settings.FB_API_ID
    template_dict['auth_page'] = 'authenticate'
    template_dict['form'] = LoginForm()
    return render_to_response('login.html',template_dict,\
        context_instance=RequestContext(request))


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
    template_dict['fb_app_id'] = settings.FB_API_ID
    template_dict['auth_page'] = 'authenticate'

    fb_user = facebook.get_user_from_cookie(request.COOKIES, \
                                            settings.FB_API_ID, \
                                            settings.FB_SECRET_KEY)

    if fb_user:
        template_dict['fb_user_detected'] = True

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
            return render_to_response('static_login.html',template_dict,\
                context_instance=RequestContext(request))
    else:
        #the user is either coming to the login page from another page
        #or they had some issues submitting input correctly
        form = LoginForm()
        template_dict['form'] = form
    return render_to_response('static_login.html',template_dict,\
        context_instance=RequestContext(request))


def register(request):
    """
    The user has chosen not to auth through facebook and doesn't already 
    have django credentials
    """
    template_dict = {}
    form = None

    return_page = ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #grab input
            logger.debug('users.views.register(request): form was valid')
            f_username = form.cleaned_data['username']
            f_password = form.cleaned_data['password']
            #f_email = form.cleaned_data['email']
            #f_first_name = form.cleaned_data['first_name']
            #f_last_name = form.cleaned_data['last_name']
            #f_street_address = form.cleaned_data['street_address']
            #f_city = form.cleaned_data['city']
            #f_state = form.cleaned_data['state']
            #f_zip_code = form.cleaned_data['zip_code']
            #f_phone = form.cleaned_data['phone']
            #f_dob = form.cleaned_data['dob']
            #we validate the username / email is unique by overriding
            #clean_field methods in RegisterForm
            baseuser = User.objects.create_user(username=f_username,\
                password=f_password, email='')
            baseuser.first_name=''
            baseuser.last_name=''
            baseuser.save()
            newuser = UserProfile(user=baseuser)
            newuser.save()
            logger.debug('user.views.register(request): user saved') 
            #this call is antiquated and not how the flow is designed to work
            #any longer.  
            #return do_login(f_username,f_password,request)
            return HttpResponseRedirect('/')
        else:
            return_page = 'users-register.html'
    if request.method != 'POST': 
        #get a new form
        form = RegisterForm()
        return_page = 'users-register.html'
    template_dict['form'] = form
    logger.debug('users.views.register(request: returning page='+return_page)
    return render_to_response(return_page, template_dict,\
        context_instance=RequestContext(request))


def api_auth(request, uri_username, output_format='json'):
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

                            # Success!
                            data['username'] = username
                        else:
                            raise UserAccountDisabled
                    else:
                        raise BadUsernameOrPassword

                else:
                    # Form didn't validate

                    # HACK ALERT: Incorrect usernames/passwords are 
                    # are checked in the validation code of user.forms.LoginForm
                    # We'll detect this and try to return a more reasonable 
                    # error message.
                    if '__all__' in form.errors.keys():
                        if form.errors['__all__'] == \
                            [form.WRONG_USERNAME_OR_PASSWORD_MSG]:
                            raise BadUsernameOrPassword( \
                                form.WRONG_USERNAME_OR_PASSWORD_MSG) 
        
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

    except BadUsernameOrPassword, error:
        status = 401 # unauthorized
        data['error'] = "%s" % error

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)


def api_users(request, output_format='json'):
    """Catch-all view for user api calls."""
    
    data = {} # Response data 
    status = 200 # Ok

    try:
        if request.is_ajax():
            if request.method == 'POST':
                # Registering a new user

                form = RegisterForm(request.POST)

                if form.is_valid():
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
                    f_dont_log_user_in = form.cleaned_data['dont_log_user_in']
                    #we validate the username / email is unique by overriding
                    #clean_field methods in RegisterForm
                    baseuser = User.objects.create_user(username=f_username,\
                        password=f_password, email=f_email)
                    baseuser.first_name=f_first_name
                    baseuser.last_name=f_last_name
                    baseuser.save()
                    newuser = UserProfile(user=baseuser, city=f_city, \
                        street_address=f_street_address, state=f_state, \
                        zip=f_zip_code, phone_number=f_phone)
                    newuser.save()

                    if not f_dont_log_user_in:

                        # Create user
                        user = authenticate(username=f_username, \
                                            password=f_password)
                        login(request, user)

                    # Set our response codes and data
                    status = 201 # Created
                    data['username'] = f_username
                    data['uri'] = '/api/%s/users/%s/' % (output_format, \
                        f_username)

                else:
                    # Form didn't validate

                    # HACK ALERT: Conflicting usernames/emails 
                    # are checked in the validation code of user.forms.RegisterForm
                    # We'll detect this and try to return a more reasonable 
                    # error message.
                    if 'username' in form.errors.keys():
                        if form.errors['username'] == \
                           [form.USERNAME_EXISTS_MSG]:
                            raise UserUsernameExists(form.USERNAME_EXISTS_MSG) 

                    if 'email' in form.errors.keys():
                        if form.errors['email'] == [form.EMAIL_EXISTS_MSG]:
                            raise UserEmailExists(form.EMAIL_EXISTS_MSG) 

                    status = 400 # Bad Request
                    data['error'] = "Some required fields are missing or invalid"
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

    except NonAjaxRequest as detail:
        status = 403 # Forbidden
        data['error'] = "%s" % detail 

    except (UserUsernameExists, UserEmailExists) as detail:
        status = 409 # Conflict
        data['error'] = "%s" % detail 

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)


def api_facebook_auth(request, output_format='json'):
    """Authenticate a user who is already logged into Facebook into the site."""

    #logger.debug("entering api_facebook_auth()")

    data = {} # Response data 
    status = 200 # Ok

    # Check to see if there's a cookie indicating that the user
    # is logged in with Facebook.
    fb_user = facebook.get_user_from_cookie(request.COOKIES, \
                                            settings.FB_API_ID,\
                                            settings.FB_SECRET_KEY)

    try:
        if fb_user:
            try:
                user_profile =  UserProfile.objects.get(\
                    facebook_user_id=fb_user['uid'])

            except UserProfile.DoesNotExist:
                #they're not, so we need to create them and move em along
                fb_graph = facebook.GraphAPI(fb_user['access_token'])
                fb_profile = fb_graph.get_object("me")
                username = fb_profile['first_name'] + fb_profile['last_name']
                password = fb_profile['id']
                base_user = User.objects.create_user(username=username,\
                                                     password=password, email='na')
                user_profile = UserProfile(user=base_user,\
                                               facebook_user_id=fb_profile['id'])
                user_profile.save()

            finally:
                # Log the user in without authenticating them
                # See http://zcentric.com/2010/05/12/django-fix-for-user-object-has-no-attribute-backend/
                user_profile.user.backend = \
                    'django.contrib.auth.backends.ModelBackend'
                login(request, user_profile.user)
                #logger.debug("User %s logged in." % (user_profile.user))

                # Set up our return data
                data['username'] = user_profile.user.username 
                data['uri'] = '/api/%s/users/%s/' % (output_format, \
                    user_profile.user.username)

        else:
            raise NoFacebookUser

    except NoFacebookUser as detail:
        status = 401 # unauthorized
        data['error'] = "%s" % error

    return HttpResponse(content=json.dumps(data), mimetype='application/json',
                        status=status)

def api_invite(request, output_format='json'):
    """Create a user, but make it disabled.

    Formats: json

    HTTP Method: GET

    Requires authentication: false

    Parameters:

    * email: E-mail address for the new user. 
    """

    status = 201 # HTTP return status.  We'll be optimistic.
    data = {} # response data 

    try:
        if request.method == 'POST':
            form = InviteForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']

                try:
                    user = User.objects.get(email=email)
                    raise UserEmailExists("It looks like you've already requested an invitation.") 
                except User.DoesNotExist:
                    username = email # Username defaults to e-mail address
                    if len(email) > 30:
                        print email
                        # Django usernames can't be longer than 30 characters
                        # Just take the first 30 characters of the part of
                        # the email address before the '@'
                        email_parts = email.partition('@')
                        username = email_parts[0][:30]

                    
                    user = User.objects.create_user(username=username,
                                                    email=email)
                    user.is_active = False
                    user.set_unusable_password()
                    user.save()
                    user_profile = UserProfile(user=user)
                    user_profile.save()

            else:
                print form.errors
                status = 400 # Caught in a bad request
                data['error'] = "Invalid e-mail address."

        else:
            raise MethodUnsupported("%s is not supported at this time." % \
                                (request.method))

    except MethodUnsupported, e:
        status = 405 # Method not allowed
        data['error'] = "%s" % e

    except (UserEmailExists) as detail:
        status = 409 # Conflict
        data['error'] = "%s" % detail 

    except Exception as detail:
        status = 500 # What the what?
        data['error'] = "Something went wrong.  We're looking into it.  Please try again." 
        print detail

    content=json.dumps(data)

    return HttpResponse(content=content, mimetype='application/json', \
                        status=status)
