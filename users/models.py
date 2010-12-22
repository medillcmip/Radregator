from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extra user data.
    
    Fields:

    user: Django user for the profile.
    facebook_user_id: User ID from the Facebook API.  This is populated if 
                      the user chooses to register/login with Facebook.
    is_verified: User has claimed account, filled in some optional fields.
    reporter_verified: A reporter has contacted the user, probably for a story.
    interest: Interest in seeking a user account.  This is populated by the 
              signup form.

    """

    USER_TYPE_CHOICES = (
    (u'R', u'reporter'),
    (u'S', u'source'),
    (u'A', u'author'))

    INTEREST_CHOICES = (
        (u'', u'Neither or unanswered'),
        (u'publisher', u'publisher'),
        (u'consumer', u'consumer'),
    )

    user = models.ForeignKey(User)
    facebook_user_id = models.TextField(blank=True)
    street_address = models.TextField(blank=True)
    city = models.TextField(blank=True)
    state = models.CharField(blank=True, max_length=2)
    zip = models.CharField(blank=True, max_length=10)
    phone_number = models.CharField(blank=True, max_length=12)
    dob = models.DateField(blank=True, null = True)
    user_type = models.CharField(max_length=15, choices = USER_TYPE_CHOICES)
    is_verified = models.BooleanField(default = False)
    reporter_verified = models.ForeignKey("UserProfile", blank=True, null=True)
    interest = models.CharField(max_length=15, choices=INTEREST_CHOICES, 
                                default='', blank=True)

    def is_reporter(self):
        return self.user_type == u'R'

    def __unicode__(self):
        return self.user.username
