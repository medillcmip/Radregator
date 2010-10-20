from django import forms
from models import User
import datetime
from django.contrib.auth import authenticate
from django.contrib.localflavor.us.forms import USZipCodeField,\
    USStateField,USPhoneNumberField

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)
    
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
        user = authenticate(username = f_username, password = f_password)
        if user is None and (f_username != None and f_password != None):
            raise forms.ValidationError('The username / password combination you entered was wrong or you don\'t have an account with us')
        else:
            return self.cleaned_data


class RegisterForm(forms.Form):
    """
    using django.forms.ModelForm doesn't really
    fit here because the User class is a property
    of the UserProfile class... any suggestions?
    """
    
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=45, required=False)
    email = forms.EmailField(required=False)
    street_address = forms.CharField(max_length=45,required=False)
    city = forms.CharField(max_length=45,required=False)
    state = USStateField(required=False)
    zip_code = USZipCodeField(required=False)
    phone = USPhoneNumberField(required=False)
    dob = forms.DateField(initial=datetime.date.today, required=False)
    def clean_email(self):
        """
        ensure no other users have the same email
        """

        def get_non_empty_emails(usr):
            if len(usr.email) != 0: return True
            else: return False
        data = self.cleaned_data['email']
        usrs = User.objects.filter(email=data, email__isnull=False)
        populated_emails = filter(get_non_empty_emails,usrs)
        if len(populated_emails) > 0:
            raise forms.ValidationError('This email already exists, please try another')
        else:
            return data

    def clean_username(self):
        """
        ensure no other users exist with the same username
        """
        data = self.cleaned_data['username']
        usrs = User.objects.filter(username=data)
        if len(usrs) > 0:
            raise forms.ValidationError('The username is taken, please try another')
        else:
            return data
