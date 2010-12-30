from django.test import TestCase
from django.contrib.auth.models import User

from models import UserProfile

class PreviewSignupTest(TestCase):
    """Test case for API endpoint for signup form."""

    def setUp(self):
        self._endpoint_url = '/api/json/invite/'

    def test_get(self):
        email = 'foo@bar.com'
        interest = 'consumer'
        response = self.client.get(self._endpoint_url, 
            {'email' : email, 'interest': interest})
        self.assertEqual(response.status_code, 405)

    def test_blank_email(self):
        email = ''
        interest = 'consumer'
        response = self.client.post(self._endpoint_url, 
            {'email' : email, 'interest': interest})
        self.assertEqual(response.status_code, 400)

    def test_invalid_email(self):
        email = 'foo@'
        interest = 'consumer'
        response = self.client.post(self._endpoint_url, 
            {'email' : email, 'interest': interest})
        self.assertEqual(response.status_code, 400)

    def _test_interest(self, interest):
        """Utility method to test different values of the interest parameter"""
        email = 'foo@bar.com'
        response = self.client.post(self._endpoint_url, 
            {'email' : email, 'interest': interest})
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=email)
        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual(interest, user_profile.interest)

    def test_blank_interest(self):
        self._test_interest('')

    def test_publisher_interest(self):
        self._test_interest('publisher')

    def test_consumer_interest(self):
        self._test_interest('consumer')

    def test_invalid_interest(self):
        email = 'foo@bar.com'
        interest = 'asasdadad'
        response = self.client.post(self._endpoint_url, 
            {'email' : email, 'interest': interest})
        self.assertEqual(response.status_code, 400)
