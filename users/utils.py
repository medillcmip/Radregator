from users.exceptions import BadUsernameOrPassword, UserAccountDisabled, \
                             UserUsernameExists, UserEmailExists, \
                             NoFacebookUser
import core.utils


from django.core.mail import send_mail

from models import UserProfile
from models import User


def send_activation_email():
    """
    send out the activation email for users that were created during the 
    december rollout with a unique key so a form can be presented to them
    that will activate their account
    http://docs.djangoproject.com/en/dev/topics/email/
    """
    user = User.objects.get(email='shifflett.shane@gmail.com')
    send_mail('Subject here', 'Here is the message.', 'from@example.com',
        [user.email], fail_silently=False)
