import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from core.models import Summary, Topic, Comment, CommentType
import core.utils
from users.models import UserProfile


#class ApiTestCase(TestCase):
    #def setUp(self):
        #pass
#
    #def test_create_concur_response(self):
        #pass
#
    #def test_get_responses(self):
        #c = Client()
        #response = c.get('/api/json/comments/1/responses/',
                         #HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #json_content = json.loads(response.content)
        #print json_content
#
        #self.fail("Test not yet implemented.")

class BurningQuestionsTestCase(TestCase):
    fixtures = ['test_users.json', 'test_topics.json', 'comment_types.json']

    def _ask_question(self, topic, text, user_profile):
        comment_type = CommentType.objects.get(name="Question")
        question = Comment(text=text, user=user_profile, \
            comment_type=comment_type)
        question.save()
        question.topics = [topic]
        question.save()

    def _ask_initial_questions(self):
        topic = Topic.objects.all()[0]
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        self._ask_question(topic=topic, text="This is a question", \
            user_profile=user1_profile)
        self._ask_question(topic=topic, text="This is another question", \
            user_profile=user2_profile)
        self._ask_question(topic=topic, text="This is yet another question", \
            user_profile=user3_profile)
        self._ask_question(topic=topic, text="This is a fourth question", \
            user_profile=user4_profile)
        self._ask_question(topic=topic, text="This is a fifth question", \
            user_profile=user5_profile)

    def setUp(self):
        self._ask_initial_questions()
