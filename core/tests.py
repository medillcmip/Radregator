import json
import unittest

from django.test import Client

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_responses(self):
        c = Client()
        response = c.get('/api/json/comments/1/responses/',
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(client.content)

        fail("Test not yet implemented.")

