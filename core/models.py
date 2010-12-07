from django.db import models
from django.contrib.sites.models import Site

from utils import comment_cmp, CountIfConcur
from clipper.models import Article
from clipper.models import Clip
from tagger.models import Tag
from users.models import UserProfile

class SummaryManager(models.Manager):
    def get_by_natural_key(self, text):
        return self.get(text=text)

class Summary(models.Model):
    """Summary of a subject (likely a Topic).  Make this a separate class
       if we want to do versioning."""
    text = models.TextField(blank=True, unique = True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.text[:80]

    def natural_key(self):
        return self.text

    class Meta:
        verbose_name_plural = 'Summaries'

class Topic(models.Model):
    """A subject of discussion.  An information silo.  These will generally
       correspond to a page on the front end that will aggregate
       comments and other content around the subject.  This might
       be something like 'Evanston Libraries'

       Fields:

       slug: A shortened, space-replaced, weird character cleaned 
                    version of the title.  This will get used in the URL
                    paths to views related to a given topic.
       topic_tags: Content with any of these tags can get pulled into a topic 
                   view.
       curators: Users who have priveleges to update this topic.
       summary: Short (1-2) paragraph description of the topic, maintained
                by one of the curators.
       articles: Articles (probably recent ones) to display on the front page, selected by curators. Probably ancestors of timeline."""
    title = models.CharField(max_length=80, unique = True) 
    slug = models.SlugField(unique = True)
    summary = models.ForeignKey(Summary)
    topic_tags = models.ManyToManyField(Tag, null=True, blank=True) 
    curators = models.ManyToManyField(UserProfile)
    articles = models.ManyToManyField(Article, blank=True)
    is_deleted = models.BooleanField(default = False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

    def recursive_traverse(self, comment, level = 1):
        # Pass through comment replies, showing
        retlist = [comment]
        for child in sorted(comment.comment_set.filter(is_deleted=False, is_parent=True, topics=self), cmp=comment_cmp):
            retlist += [self.recursive_traverse(child, level+1)]
        return retlist

    def comments_to_show(self, cmp_function=comment_cmp):
        # Comment refers to the parent
        rootset = sorted(self.comments.filter(is_deleted=False, is_parent=True, related=None), cmp=cmp_function)


        treemap = {}
        allcomments = rootset

        indentlist = []

        for comment in rootset:
            indentlist += [self.recursive_traverse(comment)]

        return indentlist

    def get_questions(self):
        """Return a QuerySet containing visible questions for this topic."""
        return self.comments.filter(is_deleted=False, \
            comment_type__name="Question")

    def burning_questions(self):
        """Return a list containing burning questions."""

        if not ("_burning_questions" in self.__dict__):
            # HACK ALERT!: This is a really naive approach and should definitely be refactored in
            # the future.

            # TODO: Now that I've implemented core.utils.CountIfConcur, it might
            # be possible to refactor this.  
            # -Geoff <geoffhing@gmail.com> 2010-12-06
            burning_questions = [] 
            burning_question_ids = []
            questions = self.get_questions()
            total_positive_responses = 0

            if questions.count() > 0:
                for question in questions:
                    question.num_positive_responses = \
                        question.num_responses("concur")
                    total_positive_responses = total_positive_responses + \
                        question.num_positive_responses

                # Get average number of positive responses (be sure to cast to 
                # a float)
                avg_positive_responses = \
                    total_positive_responses / float(questions.count())

                # Now that we have the average, let's see if the questions are
                # above average. We have to loop through and re-get the response
                # counts for each question again.
                for question in questions:
                    if question.num_positive_responses > 0 and \
                       question.num_positive_responses >= avg_positive_responses and \
                       not question.is_answered():
                       question.is_burning = True
                       burning_questions.append(question)
                       burning_question_ids.append(question.id)

            self._burning_questions = burning_questions
            self._burning_question_ids = burning_question_ids

        return self._burning_questions

    def burning_question_ids(self):
        if not ("_burning_question_ids" in self.__dict__):
            # We haven't calculated our burning questions yet.  Do this.
            self.burning_questions()

        return self._burning_question_ids

    def question_is_burning(self, question):
        """ Test whether a question is burning. """
        if not ("_burning_questions" in self.__dict__):
            # We haven't calculated our burning questions yet.  Do this.
            self.burning_questions()

        return question.id in self._burning_question_ids

    def top_answers(self):
        """Return a list of top answers for a topic."""
        if not ("_top_answers" in self.__dict__):
            top_answers = [] 
            top_answer_ids = []
            questions = self.get_questions()
            total_positive_responses = 0

            if questions.count() > 0:
                # HACK ALERT: This is a very naive approach to figuring out
                # these averages.  I imagine there's a way to do this using
                # Django's ORM and aggregation.  However, it's non-trivial,
                # so I'm doing it this way to get things working.
                # - Geoff <geoffhing@gmail.com> 2010-11-18

                # We're going to calculate the average positive responses to
                # all of the answers.  First, we have to find all the answers.
                num_answers = 0
                total_positive_responses = 0

                for question in questions:
                    answers = question.get_answers()
                    num_answers += len(answers)

                    for answer in answers:
                        total_positive_responses += \
                            answer.num_responses("concur")

                # Get average number of positive responses (be sure to cast to 
                # a float)
                avg_positive_responses = 0
                if num_answers > 0:
                    avg_positive_responses = \
                        total_positive_responses / float(num_answers)

                # Now that we have the average, let's see if the answers are
                # above average. We have to loop through and re-get the response
                # counts for each question again.
                for question in questions:
                    answers = question.get_answers()

                    for answer in answers:
                        num_positive_responses = answer.num_responses("concur")

                        if num_positive_responses > 0 and \
                        num_positive_responses > avg_positive_responses:
                            answer.is_top_answer = True
                            top_answers.append(answer)
                            top_answer_ids.append(answer.id)

            self._top_answers = top_answers
            self._top_answer_ids = top_answer_ids


        return self._top_answers

    def popular_comments(self, num=5):
        """
        Return a queryset containing the num most popular comments.

        This includes questions, answers and replies.  Most popular means the
        number of responses.

        """
        return self.comments.annotate(\
            num_responses=CountIfConcur('responses')).order_by('-num_responses')[:num]

    def user_responded_comment_ids(self, user_profile, response_type):
        """
        Returns a queryset containing all ids of comments for this topic for which 
        a user has responded in a certain way.

        """
        comments = CommentResponse.objects.filter(user=user_profile, \
            type=response_type).values_list('comment', flat=True)


        return comments

    def user_voted_comment_ids(self, user_profile):
        """ 
        Returns a queryset containing all comment ids for this topic on which a
        user has voted.
        
        """
        return self.user_responded_comment_ids(user_profile=user_profile, \
            response_type='concur')

class Comment(models.Model):
    """User-generated feedback to the system.  These will implement questions,
       answers, concerns and replies.

       Fields:

       related: Comments that are related to this comment, e.g. an answer to
                a question, a re-phrasing of a comment, a question about
                a comment, or something that is just conceptually related.
       sites: Sites which this content can appear on.  This is anticipating
              sharing content between multiple sites, e.g. a Chicago
              election site and an Evanston local news site.
       comment_type: Question, concern, respsonse ...
       topics: Topics to which this comment relates.
       sources: different from a comment you own; these are comments you're associated with
       where that user may not even be an active user in the database. We'll set to is_active=False, to 
       reflect, e.g., MOS interviews. Will set up claiming process so these users can BECOME active by entering contact
       info, etc.
       is_parent: after several comments are merged, one becomes the parent. By default, this is the only one shown. Defaults
       to true, since comment is assumed to be its own parent when it's independent/visible."""
    text = models.TextField()
    user = models.ForeignKey(UserProfile, related_name="comments")
    sources = models.ManyToManyField(UserProfile, related_name = "sourced_comments", blank=True, null = True)
    tags = models.ManyToManyField(Tag, null=True, blank=True) 
    related = models.ManyToManyField("self", through="CommentRelation", 
                                     symmetrical=False, null=True)
    sites = models.ManyToManyField(Site, blank=True)
    comment_type = models.ForeignKey("CommentType")
    topics = models.ManyToManyField("Topic", blank=True, related_name = 'comments')
    responses = models.ManyToManyField(UserProfile, through="CommentResponse", 
                                       symmetrical=False, null=True,
                                       related_name="responses")
    is_parent = models.BooleanField(default = True)
    is_deleted = models.BooleanField(default = False)
    date_created = models.DateTimeField(auto_now_add=True)

    clips = models.ManyToManyField(Clip, blank=True, null=True)

    def __unicode__(self):
        return self.text[:80]

    def num_responses(self, response_type):
        return CommentResponse.objects.filter(comment=self, \
            type=response_type).count()

    def num_upvotes(self):
        return self.num_responses("concur")

    def get_related(self, relation_type):
        """Return a list of related comments of a specified type.""" 
        related_comments = []
        for relation in CommentRelation.objects.filter(right_comment=self, \
            relation_type=relation_type):
            related_comments.append(relation.left_comment)

        return related_comments

    def get_answers(self):
        """Return a list of answers for this comment (if it's a question)"""
        # TODO: Make the comment relation a constant or something.
        return self.get_related("reply")

    def num_related(self, relation_type):
        return len(self.get_related(relation_type))

    def num_answers(self):
        # TODO: Make the comment relation a constant or something.
        return self.num_related("reply")

    def is_answered(self):
        return self.num_answers() > 0


class CommentTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class CommentType(models.Model):
    """Type of comment, e.g. question, concern, answer ...  This is a separate
       class so we can easily add new types of comments."""
    name = models.CharField(max_length=15)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return self.name

class CommentRelation(models.Model):
    """Extra information about the relationship between two comments.
    see http://docs.djangoproject.com/en/1.2./topics/db/models/#extra-fields-on-many-to-many-relationships"""
    left_comment = models.ForeignKey(Comment, related_name='+') 
    # Don't need to create an inverse relation
    right_comment = models.ForeignKey(Comment, related_name='+')
    # Don't need to create an inverse relation
    relation_type = models.CharField(max_length=15)

class CommentResponse(models.Model):
    """User response to a comment.

       These are responses that are not other comments.  This will
       implement the 'I also have this question' or 'I share this concern'
       functionality.  You can think of it as implementing Facebook 'like'
       style features."""

    COMMENT_RESPONSE_CHOICES = (
        ('share', 'I share this concern'),
        ('have', 'I have this question'),
        ('like', 'I like this'),
        ('concur', 'I concur'),
        ('opinion', 'This answer is primarily opinion'),
        ('accept', 'I accept this as the best answer'),
    )

    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(UserProfile)
    type = models.CharField(max_length=20, choices=COMMENT_RESPONSE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s %s" % (self.user, self.type, self.comment) 
