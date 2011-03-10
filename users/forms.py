from django import forms
from models import User
from models import UserProfile
import datetime
import core.utils
from django.contrib.auth import authenticate
from django.contrib.localflavor.us.forms import USZipCodeField,\
    USStateField,USPhoneNumberField
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from registration.forms import RegistrationForm

logger = core.utils.get_logger(__name__) 



class LoginForm(forms.Form):
    # Error message constants 
    WRONG_USERNAME_OR_PASSWORD_MSG = 'The username / password combination ' + \
        'you entered was wrong or you don\'t have an account with us'
    ERR_ALPHANUMS_MSG = 'Usernames must be alphanumeric (i.e., A-Z, 0-9)'

    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)
    
    def clean(self):
        """ 
        we will check authentication here because this is the final step
        the views.do_login(username,password,request) function has a similar
        step, but this appears to be the cleanest way to deal with a django
        account that doesn't exist or that gave invalid input through a web
        form while also allowing FB auth
        """
        f_username = self.cleaned_data.get('username')
        f_password = self.cleaned_data.get('password')

        logger.info('LoginForm.clean(self): logging user in %s', f_username)
        user = authenticate(username = f_username, password = f_password)
    
        if user is None and (f_username != None and f_password != None):
            raise forms.ValidationError(self.WRONG_USERNAME_OR_PASSWORD_MSG)
        else:
            return self.cleaned_data

class ActivateUnactivatedForm(forms.Form):
    """
    form to activate an unactivated user from the dec signup period
    """

    USERNAME_EXISTS_MSG = 'The username is taken, please try another'
    EMAIL_EXISTS_MSG = 'This email already exists, please try another'
    USERNAME_MUST_BE_ALNUM_MSG = 'Usernames must be alphanumeric (i.e., A-Z,0-9)'
    username = forms.CharField(max_length=30,label="Username (optional: you can enter a new username)" )
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=30, widget=forms.PasswordInput)
    lookup_key = forms.CharField(widget=forms.HiddenInput)



    def clean_username(self):
        """
        ensure no other users exist with the same username
        """
        data = self.cleaned_data['username']
        logger.info('ActivateUnactivatedForm.clean_username(self): checking username %s'
            , data)
        usrs = User.objects.filter(username=data)
        if len(usrs) > 0:
            if len(usrs) > 1 and usrs[0].username != data:
                raise forms.ValidationError(self.USERNAME_EXISTS_MSG)
        else:
            return data

    def clean(self):
        """ Ensure that password and confirm_password fields match. """
        cleaned_data = self.cleaned_data
        logger.info('ActivateUnactivatedForm.clean(self): ensuring match between password \
            fields for user %s', cleaned_data.get('username'))
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class RegisterForm(RegistrationForm):
    """
    using django.forms.ModelForm doesn't really
    fit here because the User class is a property
    of the UserProfile class... any suggestions?
    """
  
    # Error message constants
    USERNAME_EXISTS_MSG = 'The username is taken, please try another'
    EMAIL_EXISTS_MSG = 'This email already exists, please try another'
    USERNAME_MUST_BE_ALNUM_MSG = 'Usernames must be alphanumeric (i.e., A-Z,0-9)'

    STATE_CHOICES = list(STATE_CHOICES)

    first_name = forms.CharField(max_length=30, required=False \
        , label='First name: (optional)')
    last_name = forms.CharField(max_length=45, required=False \
        , label='Last name: (optional)')
    street_address = forms.CharField(max_length=45,required=False \
        , label='Street: (optional)')
    city = forms.CharField(max_length=45,required=False \
        , label='City: (optional)')
    state = USStateField(required=False \
        , label='State: (optional)' \
        , widget=forms.Select(choices=STATE_CHOICES))
    zip_code = USZipCodeField(required=False \
        , label='Zip code: (optional)')
    phone = USPhoneNumberField(required=False \
        , label='Phone: (optional)')
    dob = forms.DateField(initial=datetime.date.today, required=False \
        , label='Birthday: (optional)'
        , widget=forms.TextInput(attrs={'class':'demo'}))

    def clean_email(self):
        """
        ensure no other users have the same email
        """
        def get_non_empty_emails(usr):
            if len(usr.email) != 0: return True
            else: return False
        data = self.cleaned_data['email']

        logger.info('RegisterForm.clean_email(self): checking for email %s '\
            , data)
        usrs = User.objects.filter(email=data, email__isnull=False)
        populated_emails = filter(get_non_empty_emails,usrs)
        if len(populated_emails) > 0:
            raise forms.ValidationError(self.EMAIL_EXISTS_MSG)
        else:
            return data

    def clean_username(self):
        """
        ensure no other users exist with the same username
        """
        data = self.cleaned_data['username']
        logger.info('RegisterForm.clean_username(self): checking username %s'
            , data)
        usrs = User.objects.filter(username=data)
        if len(usrs) > 0:
            raise forms.ValidationError(self.USERNAME_EXISTS_MSG)
        else:
            return data

    def clean(self):
        """ Ensure that password and confirm_password fields match. """
        cleaned_data = self.cleaned_data
        logger.info('RegisterForm.clean(self): ensuring match between password \
            fields for user %s', cleaned_data.get('username'))
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class InviteForm(forms.Form):
    email = forms.EmailField(max_length=254)
    interest = forms.ChoiceField(required=False,
        choices=(
            ('publisher', 'A publisher, reporter or other media maker interested in running Sourcerer on my site.'),
            ('consumer', 'A media consumer interested in using Sourcerer.'),
            ('', "None of these.  I'm just interested."),
        ))
