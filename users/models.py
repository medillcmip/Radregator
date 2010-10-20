from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    """Extra user data.
    
    Fields:

    facebook_user_id: User ID from the Facebook API.  This is populated if 
                      the user chooses to register/login with Facebook.
    is_verified: User has claimed account, filled in some optional fields.
    reporter_verified: A reporter has contacted the user, probably for a story.
    """

    user_type_choices = (
    (u'R', u'reporter'),
    (u'S', u'source'))
    user = models.ForeignKey(User)

    def is_reporter(self):
        return self.user_type == u'R'

    facebook_user_id = models.TextField(blank=True)
    street_address = models.TextField(blank=True)
    city = models.TextField(blank=True)
    state = models.CharField(blank=True, max_length=2)
    zip = models.CharField(blank=True, max_length=10)
    phone_number = models.CharField(blank=True, max_length=10)
    dob = models.DateField(blank=True, null = True)

    user_type = models.CharField(max_length=15, choices = user_type_choices)
    is_verified = models.BooleanField(default = False)
    reporter_verified = models.ForeignKey("UserProfile", blank=True, null=True)


    def __unicode__(self):
        return self.user.username
