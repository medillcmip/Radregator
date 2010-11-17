import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from core.models import Summary, Topic, Comment, CommentType, \
    CommentRelation, CommentResponse
import core.utils
from users.models import UserProfile
from clipper.models import Article
import clipper.views


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

class QuestionTestCase(TestCase):
    """ Base class for TestCases that deal with questions and answers. """
    fixtures = ['test_users.json', 'test_topics.json', 'comment_types.json']

    def _ask_question(self, topic, text, user_profile):
        comment_type = CommentType.objects.get(name="Question")
        question = Comment(text=text, user=user_profile, \
            comment_type=comment_type)
        question.save()
        question.topics = [topic]
        question.save()
        self._questions.append(question)

        return question

    def _answer_question(self, user_profile, question, clip_url, clip_text, \
        comment_text):
        comment_type = CommentType.objects.get(name="Reply")
        clipper.views.create_article(clip_url)
        article = Article.objects.get(url=clip_url)
        clip = clipper.models.Clip(article=article, \
            text = clip_text, user=user_profile, user_comments=comment_text)
        clip.save()
        answer = core.models.Comment(text=comment_text, \
            user=user_profile, comment_type=comment_type, is_parent=True,\
            is_deleted=False)
        answer.save()
        answer.topics = question.topics.all()
        answer.clips.add(clip)
        answer.save()

        reply_relation = core.models.CommentRelation(\
            left_comment = answer, right_comment=question,\
            relation_type = 'reply')
        reply_relation.save()

    def _respond_positively(self, user_profile, question):
        """Utility method to respond positively to a question."""
        comment_response = CommentResponse(user=user_profile, \
                                           comment=question, \
                                           type="concur")
        comment_response.save()
        
    def setUp(self):
        self._questions = []
        self._topic = Topic.objects.all()[0]

class BasicQuestionTestCase(QuestionTestCase):
    def test_num_answers(self):
        topic = self._topic

        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        question = self._ask_question(topic=topic, text="How many wards is Chinatown in?", \
            user_profile=user1_profile)
        self._answer_question(user_profile=user2_profile, question=question, \
            clip_url="http://chicagojournal.com/news/04-28-2010/Boundary_lines", \
            clip_text="Chinatown, Bridgeport and McKinley Park - home to much of the city's Chinese-descended and immigrant populations - are politically fragmented, split between four city wards, four state representative districts, three state senate districts and three U.S. congressional districts.", \
            comment_text="Chinatown is split between four wards.")
        self._answer_question(user_profile=user3_profile, question=question, \
            clip_url="http://www.chicagojournal.com/News/10-20-2010/Daley%27s_departure_opens_door_for_competitive_25th_Ward_race", \
            clip_text="Candidates have until the third week of November to file papers with City Hall - in 2007, six candidates ran for 25th Ward Alderman with Morfin finishing second. The 25th Ward is made up of the predominantly Latino Pilsen neighborhood where Solis and his two initial challengers all reside. But it also includes parts of Chinatown, Little Italy and the Tri-Taylor area. ", \

            comment_text="I don't know, but this article says the 25th ward contains parts of Chinatown.")

        self.assertEqual(question.num_answers(), 2);

class BurningQuestionsTestCase(QuestionTestCase):
    def test_get_questions(self):
        """Test the topic.get_questions() method."""
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")
        topic = self._topic

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

        questions = self._topic.get_questions()
        self.assertEqual(questions.count(), 5)

    def test_get_burning_questions(self):
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")
        topic = self._topic

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

        question = self._questions[2]

        self._respond_positively(user1_profile, question)
        self._respond_positively(user2_profile, question)
        self._respond_positively(user4_profile, question)
        self._respond_positively(user5_profile, question)
        
        # The question should now have 4 responses 
        self.assertEqual(question.num_responses("concur"), 4)

        burning_questions = self._topic.burning_questions()

        # We only voted on one item, so there should only be one burning 
        # question
        self.assertEqual(len(burning_questions), 1)

        # And that one question should be our initial question.
        self.assertEqual(question.id, burning_questions[0].id)

    def test_get_burning_questions_one_vote(self):
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")
        topic = self._topic

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

        question = self._questions[2]

        self._respond_positively(user1_profile, question)

        burning_questions = self._topic.burning_questions()

        # We only voted on one item, so there should only be one burning 
        # question
        self.assertEqual(len(burning_questions), 1)

        # And that one question should be our initial question.
        self.assertEqual(question.id, burning_questions[0].id)

    def test_get_burning_questions_one_vote(self):
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        topic = self._topic

        self._ask_question(topic=topic, text="This is a question", \
            user_profile=user1_profile)

        question = self._questions[0]

        self._respond_positively(user2_profile, question)

        burning_questions = self._topic.burning_questions()

        # We only voted on one item, so there should only be one burning 
        # question
        self.assertEqual(len(burning_questions), 1)

        # And that one question should be our initial question.
        self.assertEqual(question.id, burning_questions[0].id)
