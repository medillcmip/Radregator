from users.exceptions import BadUsernameOrPassword, UserAccountDisabled, \
                             UserUsernameExists, UserEmailExists, \
                             NoFacebookUser
import core.utils
from django.core.mail import send_mail
from django.conf import settings
from models import UserProfile
from models import User
from models import ActivationKeyValue
from registration.models import RegistrationProfile
import os

mail_msg_one = "
Greetings from Sourcerer!

Some months ago, you indicated an interest in being a beta user of the Sourcerer \"context management system\" developed last fall by a team of journalism students at Northwestern University.

We are pleased to announce that the Sourcerer beta is ready for you to try out, and we have already registered you as a user of the site.

What’s Sourcerer?

Sourcerer is an open-source Web platform organized around topics.  It enables users to ask and answer questions about those topics.  It has a couple of novel features. First, when answering a question, users are required to include a link to the source material that supports the answer.  And second, the links provided by users are assembled into a timeline of stories that serves as an entry point for understanding the topic.  As with other Q&A sites, users can \"vote up\" questions or answers they think are particularly good.

For our beta test, we have populated the site with two real topics that you or people you know might want to know more about:
* Paid Online Content
* Cultivating Online Communities

We've also set up a third topic, called \"Sourcerer Beta,\" where you can ask questions about the Sourcerer project itself.

If you’d like a run-through of Sourcerer’s features, and an introduction to using the system, we’ve made a short video, which you can watch at http://www.youtube.com/watch?v=hXuTmmBB2-E

We want your feedback! 

We hope you will try out the site and provide us with feedback on how to improve Sourcerer.  We also are seeking your ideas for particular kinds of stories, issues or publications that would be good applications for this kind of site.

To provide us with feedback, just click on the green \"Feedback\" tab on the right side of every page. You can use this channel -- provided through the \"Get Satisfaction\" customer-service tools -- to report bugs, tell us what you like or don't like, or suggest ways you'd like Sourcerer to be used.

Using Sourcerer

To use Sourcerer, follow the link below to enter a password and, optionally, change your user name.  You will be identified on the site by the user name you select.  

If you don't provide a new user name, your user name will be your email address, which means that your questions and answers will be published with your email address attached to them.  If you prefer to use a name or handle instead, you'll want to be sure to choose a different user name after logging in.

"

mail_msg_two = "Thanks for your interest in Sourcerer.  We hope you’ll try out the site and give us feedback so we can keep making it better.

The Sourcerer Team

"

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
    users = User.objects.all()
    for usr in users:
        activation_key = os.urandom(10).encode('hex')
        akv = ActivationKeyValue(user=usr, activation_key=activation_key)
        akv.save()
        email_message_link = activation_url + activation_key + "/"
        send_mail(email_subject, email_msg_one + email_message_link +email_msg_two, email_from,
            [str(usr.email)], fail_silently=False)
