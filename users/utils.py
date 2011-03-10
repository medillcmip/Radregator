from users.exceptions import BadUsernameOrPassword, UserAccountDisabled, \
                             UserUsernameExists, UserEmailExists, \
                             NoFacebookUser
import core.utils
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from models import UserProfile
from models import User
from models import ActivationKeyValue
from registration.models import RegistrationProfile
import os


def send_activation_email():
    """
    send out the activation email for users that were created during the 
    december rollout with a unique key so a form can be presented to them
    that will activate their account
    http://docs.djangoproject.com/en/dev/topics/email/
    """
    email_subject = 'Welcome to the Sourcerer beta test!'
    email_from = 'admin@sourcerer.us'
    activation_url = settings.SITE_URL+'/activate_unactivated/'
    #emails = User.objects.raw('SELECT id, email from auth_user')
    users = User.objects.filter(is_active=False)
	plaintext = get_template('activate_users_email.txt')
    for usr in users:
        activation_key = os.urandom(10).encode('hex')
        akv = ActivationKeyValue(user=usr, activation_key=activation_key)
        akv.save()
        email_message_link = activation_url + activation_key + "/"

		d = Context({ 'activation_link': email_message_link })
		text_content = plaintext.render(d)
		msg = EmailMultiAlternatives(email_subject, text_content, email_from, [str(usr.email)])
		msg.send()
