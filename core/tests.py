import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from core.models import Summary, Topic, Comment, CommentType, \
    CommentRelation, CommentResponse
import core.utils
from users.models import UserProfile
from clipper.models import Article
import clipper.views
from core.forms import CommentSubmitForm
from clipper.forms import ClipTextForm

class BaseTestCase(TestCase):
    """Base class for test cases that provides some utility methods."""

    def _ask_question_forms(self, cmt_type_str, txt, topic, reply_to):
        form = CommentSubmitForm(data={'comment_type_str': cmt_type_str,
                                              'text': txt,
                                              'topic': topic,
                                              'in_reply_to': reply_to})
        return form

    def _answer_question_form(self, selected_text, user_comments):

        form = ClipTextForm(data={'selected_text': selected_text,
                                    'user_comments': user_comments,
                                    'url_field': 'http://google.com',
                                    'comment_id_field': '1',
                                    'topic_id_field': '1'})
        return form

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

        return answer

    def _respond_positively(self, user_profile, question):
        """Utility method to respond positively to a question."""
        comment_response = CommentResponse(user=user_profile, \
                                           comment=question, \
                                           type="concur")
        comment_response.save()

    def _flag_as_opinion(self, user_profile, question):
        """Utility method to flag something as opinion."""
        comment_response = CommentResponse(user=user_profile, \
                                           comment=question, \
                                           type="opinion")
        comment_response.save()

    def _create_topic(self, title, summary_text):
        summary = Summary.objects.get_or_create(text=summary_text)[0] 
        summary.save()
        topic = Topic(title = title, slug = core.utils.slugify(title), 
                      summary = summary, is_deleted = False)
        topic.save()
        return topic
        
    def setUp(self):
        self._questions = []


class QuestionTestCase(BaseTestCase):
    """Base class for test cases that provides some default users and topics."""
    fixtures = ['test_users.json', 'test_topics.json', 'comment_types.json']

    def setUp(self):
        # Call the parent's setUp method.
        super(QuestionTestCase, self).setUp()

        # Make the first topic we created (in the fixture) easily accessible.
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


        #test invalid inputs
        q_txt = "<iframe title=\"YouTube video player\" \
        class=\"youtube-player\" type=\"text/html\" width=\"640\" \
        height=\"390\" src=\"http://www.youtube.com/embed/54R2p0Vb87M?rel=0\"\
         frameborder=\"0\"></iframe> test<b> test</b> <img> src </img>"
        question_form = self._ask_question_forms('1', q_txt, '3', '3')
        self.assertTrue(question_form.is_valid())
        self.assertEquals(question_form.cleaned_data['text'], 
            u' test test  src ')

        answer_form = self._answer_question_form(q_txt,q_txt)
        self.assertTrue(answer_form.is_valid())

        self.assertEquals(answer_form.cleaned_data['selected_text'], 
            u' test test  src ')


        self.assertEquals(answer_form.cleaned_data['user_comments'], 
            u' test test  src ')

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

class TopAnswersTestCase(QuestionTestCase):
    def test_one_question_no_answers(self):
        topic = self._topic

        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        question = self._ask_question(topic=topic, text="How many wards is Chinatown in?", \
            user_profile=user1_profile)

        top_answers = topic.top_answers()
        
        self.assertEqual(len(top_answers), 0);

    def test_one_question_one_answer_no_upvotes(self):
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

        top_answers = topic.top_answers()
        
        self.assertEqual(len(top_answers), 0);

    def test_one_question_two_answers_no_upvotes(self):
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

        top_answers = topic.top_answers()
        
        self.assertEqual(len(top_answers), 0);

    def test_one_question_one_answer_one_upvote(self):
        topic = self._topic

        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        question = self._ask_question(topic=topic, text="How many wards is Chinatown in?", \
            user_profile=user1_profile)
        answer = self._answer_question(user_profile=user2_profile, question=question, \
            clip_url="http://chicagojournal.com/news/04-28-2010/Boundary_lines", \
            clip_text="Chinatown, Bridgeport and McKinley Park - home to much of the city's Chinese-descended and immigrant populations - are politically fragmented, split between four city wards, four state representative districts, three state senate districts and three U.S. congressional districts.", \
            comment_text="Chinatown is split between four wards.")

        self._respond_positively(user3_profile, answer)

        top_answers = topic.top_answers()
        
        self.assertEqual(len(top_answers), 0);

    def test_one_question_two_answers_one_upvote_each(self):
        topic = self._topic

        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        question = self._ask_question(topic=topic, text="How many wards is Chinatown in?", \
            user_profile=user1_profile)
        answer1 = self._answer_question(user_profile=user2_profile, question=question, \
            clip_url="http://chicagojournal.com/news/04-28-2010/Boundary_lines", \
            clip_text="Chinatown, Bridgeport and McKinley Park - home to much of the city's Chinese-descended and immigrant populations - are politically fragmented, split between four city wards, four state representative districts, three state senate districts and three U.S. congressional districts.", \
            comment_text="Chinatown is split between four wards.")
        answer2 = self._answer_question(user_profile=user3_profile, question=question, \
            clip_url="http://www.chicagojournal.com/News/10-20-2010/Daley%27s_departure_opens_door_for_competitive_25th_Ward_race", \
            clip_text="Candidates have until the third week of November to file papers with City Hall - in 2007, six candidates ran for 25th Ward Alderman with Morfin finishing second. The 25th Ward is made up of the predominantly Latino Pilsen neighborhood where Solis and his two initial challengers all reside. But it also includes parts of Chinatown, Little Italy and the Tri-Taylor area. ", \

            comment_text="I don't know, but this article says the 25th ward contains parts of Chinatown.")

        self._respond_positively(user3_profile, answer1)
        self._respond_positively(user4_profile, answer2)

        top_answers = topic.top_answers()
        
        self.assertEqual(len(top_answers), 0);

    def test_one_question_two_answers_different_upvotes(self):
        topic = self._topic

        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        question = self._ask_question(topic=topic, text="How many wards is Chinatown in?", \
            user_profile=user1_profile)
        answer1 = self._answer_question(user_profile=user2_profile, question=question, \
            clip_url="http://chicagojournal.com/news/04-28-2010/Boundary_lines", \
            clip_text="Chinatown, Bridgeport and McKinley Park - home to much of the city's Chinese-descended and immigrant populations - are politically fragmented, split between four city wards, four state representative districts, three state senate districts and three U.S. congressional districts.", \
            comment_text="Chinatown is split between four wards.")
        answer2 = self._answer_question(user_profile=user3_profile, question=question, \
            clip_url="http://www.chicagojournal.com/News/10-20-2010/Daley%27s_departure_opens_door_for_competitive_25th_Ward_race", \
            clip_text="Candidates have until the third week of November to file papers with City Hall - in 2007, six candidates ran for 25th Ward Alderman with Morfin finishing second. The 25th Ward is made up of the predominantly Latino Pilsen neighborhood where Solis and his two initial challengers all reside. But it also includes parts of Chinatown, Little Italy and the Tri-Taylor area. ", \

            comment_text="I don't know, but this article says the 25th ward contains parts of Chinatown.")

        self._respond_positively(user3_profile, answer1)
        self._respond_positively(user4_profile, answer2)
        self._respond_positively(user5_profile, answer2)

        top_answers = topic.top_answers()
        
        self.assertEqual(len(top_answers), 1);

class QuestionResponseTestCase(QuestionTestCase):
    def _create_response(self, question, user_profile, response_type):
        comment_response = CommentResponse(user=user_profile, \
                                           comment=question, \
                                           type=response_type) 
        comment_response.save()

        return comment_response

    def _create_upvote(self, question, user_profile):
        return self._create_response(question, user_profile, 'concur')

    def test_user_voted_comment_ids_no_votes(self):
        topic = self._topic
        user2_profile = UserProfile.objects.get(user__username="user2")

        user_voted_comment_ids = topic.user_voted_comment_ids(user2_profile)
        self.assertEqual(len(user_voted_comment_ids), 0)
        

    def test_user_voted_comment_ids_one_vote(self):
        topic = self._topic
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")

        # Make a default question
        question = self._ask_question(topic=topic, \
            text="How many wards is Chinatown in?", \
            user_profile=user1_profile)

        # And give it one vote
        self._create_upvote(question, user2_profile)

        user_voted_comment_ids = topic.user_voted_comment_ids(user2_profile)
        self.assertEqual(len(user_voted_comment_ids), 1)
        self.assertEqual(user_voted_comment_ids[0], question.id)


class QuestionsApiTestCase(QuestionTestCase):
    #def test_get_responses(self):
        #c = Client()
        #response = c.get('/api/json/comments/1/responses/',
                         #HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #json_content = json.loads(response.content)
        #print json_content
#
        #self.fail("Test not yet implemented.")

    def test_questions_popular_no_voting_no_questions(self):
        """Test for /api/json/questions/ endpoint.
        
        Case for fetching popular questions when there are no questions.
        
        """

        c = Client()
        response = c.get('/api/json/questions/', \
                        {'result_type': 'popular', 'count': '5'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(len(json_content), 0)

    def test_questions_popular_no_voting_one_question(self):
        """Test for /api/json/questions/ endpoint.

        Case for fetching popular questions when there is one question.
        
        """

        topic = self._topic
        user1_profile = UserProfile.objects.get(user__username="user1")

        # Make a default question
        question = self._ask_question(topic=topic, \
            text="How many wards is Chinatown in?", \
            user_profile=user1_profile)

        c = Client()
        response = c.get('/api/json/questions/', \
                        {'result_type': 'popular', 'count': '5'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(len(json_content), 1)

        json_question = json_content[0]
        self.assertEqual(question.id, json_question['pk'])
        self.assertEqual(question.text, json_question['fields']['text'])

    def test_questions_popular_no_voting_multiple_questions(self):
        """Test for /api/json/questions/ endpoint.

        Case for fetching popular questions when there is more than one question.

        """

        topic = self._topic
        user1_profile = UserProfile.objects.get(user__username="user1")

        # Ask some questions 
        count = 5 # Ask 5 questions
        for i in range(count):
            question = self._ask_question(topic=topic, \
                text="Test question %d" % (i), \
                user_profile=user1_profile)

        # Get the questions from the API 
        c = Client()
        response = c.get('/api/json/questions/', \
                        {'result_type': 'popular', 'count': '5'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(len(json_content), count)

        for json_question in json_content:
            # HACK ALERT: This is a really naive search, but I wanted to just 
            # write this rather than figuring out the cleanest, most Pythonic
            # way to do this.
            question_found = False
            for question in self._questions:
                if question.id == json_question['pk'] and \
                   question.text == json_question['fields']['text']:
                   question_found = True

            self.assertEqual(question_found, True)

    def test_questions_popular_no_voting_multiple_questions_with_count(self):
        """Test for /api/json/questions/ endpoint.

        Case for fetching popular questions when there are multiple questions
        but we only want to return a few.

        """

        topic = self._topic
        user1_profile = UserProfile.objects.get(user__username="user1")

        # Ask 5 questions 
        count = 5
        for i in range(count):
            question = self._ask_question(topic=topic, \
                text="Test question %d" % (i), \
                user_profile=user1_profile)

        # Get the questions from the API, but not all 5 
        c = Client()
        response = c.get('/api/json/questions/', \
                        {'result_type': 'popular', 'count': '3'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(len(json_content), 3)

        for json_question in json_content:
            # HACK ALERT: This is a really naive search, but I wanted to just 
            # write this rather than figuring out the cleanest, most Pythonic
            # way to do this.
            question_found = False

            # Since we limited the number of questions, we should just get the 3 most recent
            for question in self._questions[2:]:
                if question.id == json_question['pk'] and \
                   question.text == json_question['fields']['text']:
                   question_found = True

            self.assertEqual(question_found, True)

    def test_questions_popular_voting_multiple_questions_with_count(self):
        """Test for /api/json/questions/ endpoint.

        Case for fetching popular questions when there are multiple questions
        and we've voted on some of them. 

        """

        topic = self._topic
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        # Ask 5 questions 
        count = 5
        for i in range(count):
            question = self._ask_question(topic=topic, \
                text="Test question %d" % (i), \
                user_profile=user1_profile)

            # Vote on the questions, based on the index
            # So, later questions will get more votes
            if i == 1:
               self._respond_positively(user2_profile, question) 
            elif i == 2:
               self._respond_positively(user2_profile, question) 
               self._respond_positively(user3_profile, question) 
            elif i == 3:
               self._respond_positively(user2_profile, question) 
               self._respond_positively(user3_profile, question) 
               self._respond_positively(user4_profile, question) 
            elif i == 4:
               self._respond_positively(user2_profile, question) 
               self._respond_positively(user3_profile, question) 
               self._respond_positively(user4_profile, question) 
               self._respond_positively(user5_profile, question) 

        # Get the questions from the API, but not all 5 
        c = Client()
        response = c.get('/api/json/questions/', \
                        {'result_type': 'popular', 'count': '3'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(len(json_content), 3)

        # Since we limited the number of questions, we should just get the 3 with the most
        # positive votes in descending order.  

        # Set our counter to the upper subscript of our questions list
        i = len(self._questions) - 1 
        for json_question in json_content:
            question = self._questions[i]
            self.assertEqual(question.id, json_question['pk'])
            self.assertEqual(question.text, json_question['fields']['text'])
            i = i - 1

    def test_questions_popular_voting_multiple_questions_with_opinion(self):
        """Test for /api/json/questions/ endpoint.

        Case for fetching popular questions when there are multiple questions
        and we've voted on some of them and flagged some as oppinion.

        This is designed to test that we're differentiating between the types
        of votes we're counting.  Specifically, this is designed to catch the
        bug in annotations in core.views.api_questions() where we're counting
        all responses to a question and not just the positive votes.  This bug
        was fixed in commit 71ec558bb3ae15ae342c97a1cd5dc79a7902c1bd. 

        """

        topic = self._topic
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        # Ask 5 questions 
        count = 5
        for i in range(count):
            question = self._ask_question(topic=topic, \
                text="Test question %d" % (i), \
                user_profile=user1_profile)

            # Vote on some questions, based on the index
            # So, later questions will get more votes
            # But, flag the first (index 0) question as opinion
            if i == 0:
               self._flag_as_opinion(user2_profile, question) 
               self._flag_as_opinion(user3_profile, question) 
               self._flag_as_opinion(user4_profile, question) 
               self._flag_as_opinion(user5_profile, question) 
            elif i == 1:
               self._respond_positively(user2_profile, question) 
            elif i == 2:
               self._respond_positively(user2_profile, question) 
               self._respond_positively(user3_profile, question) 
            elif i == 3:
               self._respond_positively(user2_profile, question) 
               self._respond_positively(user3_profile, question) 
               self._respond_positively(user4_profile, question) 
            elif i == 4:
               self._respond_positively(user2_profile, question) 
               self._respond_positively(user3_profile, question) 
               self._respond_positively(user4_profile, question) 
               self._respond_positively(user5_profile, question) 

        # Get the questions from the API, but not all 5 
        c = Client()
        response = c.get('/api/json/questions/', \
                        {'result_type': 'popular', 'count': '3'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(len(json_content), 3)

        # Since we limited the number of questions, we should just get the 3 with the most
        # positive votes in descending order.  

        # Set our counter to the upper subscript of our questions list
        i = len(self._questions) - 1 
        for json_question in json_content:
            question = self._questions[i]
            self.assertEqual(question.id, json_question['pk'])
            self.assertEqual(question.text, json_question['fields']['text'])
            i = i - 1


class TopicsApiTestCase(QuestionTestCase):
    def test_topics(self):
        """Test getting all topics from the API."""
        # Create some topics.
        # Remember, we have one topic created by default via the fixture. 
        topics = [self._topic]
        title_template = "Test Topic %d"
        summary_template = "More information about Test Topic %d"
        num_topics = 5

        # Remember, we have one topic created by default via the fixture. 
        # So we only need to create num_topics - 1 topics.
        for i in range(num_topics - 1):
            topic = self._create_topic(title=title_template % (i),
                               summary_text=summary_template % (i))
            topics.append(topic)

        # Get the topics from the API
        c = Client()
        response = c.get('/api/json/topics/', \
                        {'result_type': 'all'}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), num_topics)
        i = 0
        for topic in topics:
            self.assertEqual(json_content[i]['pk'], topic.id),
            self.assertEqual(json_content[i]['fields']['title'],
                             topic.title)
            self.assertEqual(json_content[i]['fields']['summary'],
                             str(topic.summary))
            i = i + 1
        
    def test_topics_with_count(self):
        """Test getting all topics from the API, limiting the number of results."""
        # Create some topics.
        # Remember, we have one topic created by default via the fixture. 
        topics = [self._topic]
        title_template = "Test Topic %d"
        summary_template = "More information about Test Topic %d"
        num_topics = 5

        # Remember, we have one topic created by default via the fixture. 
        # So we only need to create num_topics - 1 topics.
        for i in range(num_topics - 1):
            topic = self._create_topic(title=title_template % (i),
                               summary_text=summary_template % (i))
            topics.append(topic)

        # Get the topics from the API
        c = Client()
        count = 3
        response = c.get('/api/json/topics/', \
                        {'result_type': 'all', 'count': count}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), count)
        i = 0
        for topic in topics:
            if i < count:
                self.assertEqual(json_content[i]['pk'], topic.id)
                self.assertEqual(json_content[i]['fields']['title'],
                                 topic.title)
                self.assertEqual(json_content[i]['fields']['summary'],
                                 str(topic.summary))
            i = i + 1
        
    def test_topics_popular(self):
        """Test getting popular topics."""

        # Get some user profiles to work with
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        # Create 3 topics.
        # Remember, we have one topic created by default via the fixture. 
        num_topics = 3
        topics = [self._topic]
        title_template = "Test Topic %d"
        summary_template = "More information about Test Topic %d"

        # Remember, we have one topic created by default via the fixture. 
        # So we only need to create num_topics - 1 topics.
        for i in range(num_topics - 1):
            topic = self._create_topic(title=title_template % (i),
                               summary_text=summary_template % (i))
            # Ask 2 questions on each topic
            question1 = self._ask_question(topic, "This is a question!", 
                                           user1_profile)
            question2 = self._ask_question(topic, "This is another question!", 
                               user1_profile)

            # Give the 2nd topic's questions some votes
            if i == 0:
                self._respond_positively(user2_profile, question1)
                self._respond_positively(user2_profile, question2)
                self._respond_positively(user3_profile, question1)
                self._respond_positively(user3_profile, question2)

            # But give the 3rd topic's questions even more votes
            if i == 1:
                self._respond_positively(user2_profile, question1)
                self._respond_positively(user2_profile, question2)
                self._respond_positively(user3_profile, question1)
                self._respond_positively(user3_profile, question2)
                self._respond_positively(user4_profile, question1)
                self._respond_positively(user4_profile, question2)
                
            topics.append(topic)

        # Get 2 topics from the API, ordering by total number of votes
        # on its questions.
        c = Client()
        count = 2
        response = c.get('/api/json/topics/', \
                        {'result_type': 'popular', 'count': count}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), count)

        # After all the topic creation, questioning and voting is done,
        # the first topic has no votes for any of its questions, the second
        # topic has a total of four votes for all its questions and the third
        # topic has a total of six votes for all its questions.

        # The first topic in the returned ones should be the third topic
        # in our list of saved topics
        self.assertEqual(json_content[0]['pk'], topics[2].id)
        self.assertEqual(json_content[0]['fields']['title'],
                         topics[2].title)
        self.assertEqual(json_content[0]['fields']['summary'],
                         str(topics[2].summary))

        # The second topic in the returned ones should be the second topic
        # in our list of saved topics
        self.assertEqual(json_content[1]['pk'], topics[1].id)
        self.assertEqual(json_content[1]['fields']['title'],
                         topics[1].title)
        self.assertEqual(json_content[1]['fields']['summary'],
                         str(topics[1].summary))


    def test_topics_active(self):
        """Test getting active topics."""
        # Get some user profiles to work with
        user1_profile = UserProfile.objects.get(user__username="user1")
        user2_profile = UserProfile.objects.get(user__username="user2")
        user3_profile = UserProfile.objects.get(user__username="user3")
        user4_profile = UserProfile.objects.get(user__username="user4")
        user5_profile = UserProfile.objects.get(user__username="user5")

        # Create 3 topics.
        # Remember, we have one topic created by default via the fixture. 
        num_topics = 3
        topics = [self._topic]
        title_template = "Test Topic %d"
        summary_template = "More information about Test Topic %d"

        # Remember, we have one topic created by default via the fixture. 
        # So we only need to create num_topics - 1 topics.
        for i in range(num_topics - 1):
            topic = self._create_topic(title=title_template % (i),
                               summary_text=summary_template % (i))
            # Ask 2 questions on each topic
            question1 = self._ask_question(topic, "This is a question!", 
                                           user1_profile)
            question2 = self._ask_question(topic, "This is another question!", 
                               user1_profile)
            topics.append(topic)

        # Get 2 topics from the API, ordering by activity.
        # of its questions.
        c = Client()
        count = 2
        response = c.get('/api/json/topics/', \
                        {'result_type': 'active', 'count': count}, \
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), count)

        # The topics should be returned in the opposite of the order that we
        # created them since the timestamp on the questions will be slightly
        # later.

        # The first topic in the returned ones should be the third topic
        # in our list of saved topics
        self.assertEqual(json_content[0]['pk'], topics[2].id)
        self.assertEqual(json_content[0]['fields']['title'],
                         topics[2].title)
        self.assertEqual(json_content[0]['fields']['summary'],
                         str(topics[2].summary))

        # The second topic in the returned ones should be the second topic
        # in our list of saved topics
        self.assertEqual(json_content[1]['pk'], topics[1].id)
        self.assertEqual(json_content[1]['fields']['title'],
                         topics[1].title)
        self.assertEqual(json_content[1]['fields']['summary'],
                         str(topics[1].summary))

class LoggingTestCase(TestCase):
    def _get_random_directory_name(self):
        import random
        import math
        import tempfile
 
        random_number = math.trunc(random.random() * 1000)
        random_dir = "%s/sourcerer-%d" % (tempfile.gettempdir(),
                                               random_number)
        
        return random_dir

    def _get_nonexistant_directory_name(self):
        from os.path import isdir

        nonexistant_dir = self._get_random_directory_name() 

        while isdir(nonexistant_dir): 
            nonexistant_dir = self._get_random_directory_name() 

        return nonexistant_dir

    def setUp(self):
        pass

    def test_log_filename_not_writeable(self):
        from core.utils import get_logger

        filename = "%s/sourcerer.log" % self._get_nonexistant_directory_name()

        try:
            logger = get_logger('test', filename)
        except IOError:
            # We should catch the IO error in get_logger()
            self.fail("IOError exception not raised for nonexistant logfile directory.")
           
    def test_logfile_created(self):
        from tempfile import mkdtemp
        from core.utils import get_logger
        from os.path import isfile

        filename = "%s/sourcerer.log" % mkdtemp() 
        logger = get_logger('test', filename)

        if not isfile(filename):
            self.fail("Log file %s not created by get_logger()" % filename)
        

    def test_log_error(self):
        from core.utils import get_logger
        from os.path import isfile
        from tempfile import mkdtemp

        filename = "%s/sourcerer.log" % mkdtemp() 

        logger = get_logger('test', filename)

        error_msg = "This is an error."

        logger.error(error_msg)

        f = open(filename)
        line = f.readline()

        # The most recent log entry in the file should contain our error message
        self.assertNotEqual(line.find(error_msg), -1)
