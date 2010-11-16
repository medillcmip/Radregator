import json
import unittest

from django.test import Client

from core.models import Summary, Topic
import core.utils

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_concur_response(self):
        pass

    def test_get_responses(self):
        c = Client()
        response = c.get('/api/json/comments/1/responses/',
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)
        print json_content

        self.fail("Test not yet implemented.")

class BurningQuestionsTestCase(inittest.TestCase):
    def setUp(self):
        pass
