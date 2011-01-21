from django import forms
from django.forms.widgets import Select, HiddenInput
from core.models import Comment,CommentType,Topic
from tagger.models import Tag
from users.models import UserProfile
from django.forms.widgets import CheckboxSelectMultiple
from core import utils

logger = utils.get_logger()

class CommentDeleteForm(forms.Form):
    allcomments = Comment.objects.filter(is_deleted=False).filter(is_parent=True)
    comments = forms.ModelMultipleChoiceField(allcomments, )


class CommentTopicForm(forms.Form):
    allcomments = Comment.objects.filter(is_deleted=False).filter(is_parent=True)
    alltopics = Topic.objects.filter(is_deleted=False)
    comment = forms.ModelChoiceField(allcomments, empty_label = None)
    topic = forms.ModelChoiceField(alltopics, empty_label = None)

    
class TopicDeleteForm(forms.Form):
    alltopics = Topic.objects.filter(is_deleted=False)
    topics = forms.ModelMultipleChoiceField(alltopics, )


class NewSummaryForm(forms.Form):
    """ Form to let a user create a new summary for a topic"""

    alltopics = Topic.objects.filter(is_deleted=False)
    topic = forms.ModelChoiceField(alltopics, )
    summary_text = forms.CharField(required = True, widget = forms.TextInput)


class NewTopicForm(forms.ModelForm):
    # Comment to source from should default to null
    # Really just using the modelform to validate the title as new
    summary_text = forms.CharField(required = True )
    allcomments = Comment.objects.filter(is_deleted=False).filter(is_parent=True)
    source_comment = forms.ModelChoiceField(allcomments, required = False)

    class Meta:
        model = Topic
        fields = ('title', 'summary_text', 'source_comment')


class MergeCommentForm(forms.Form):
    """ Take a set of comments, designate one as parent."""

    allcomments = Comment.objects.filter(is_deleted = False).filter(is_parent = True)
    comments = forms.ModelMultipleChoiceField(allcomments)
    parent = forms.ModelChoiceField(allcomments, empty_label = None)


def initial_topic_title():
    """ 
    Workaround to set initial value for topic field of CommentSubmitForm

    This handles the case when there are no topics.   

    """
    
    if Topic.objects.count() > 0:
        title = Topic.objects.all()[0].title
    else:
        title = ''

    return title 


class CommentSubmitForm(forms.Form):
    """
    Form to let a user submit a comment tied to a particular topic.  Using 
    the names since those already get accessed in the template; the alternative 
    would be to use a ModelChoiceField with a HiddenInput widget, and make 
    jQuery handle changing the topic based on clicking on tabs. It will be 
    possible to simplify this if the UI changes to allow the user to explicitly 
    select a topic or topics (presumably using a ModelMultipleChoiceField).

    Could switch comment_type_str to use a ModelChoiceField on 
    CommentType.objects.all(). It's difficult to make this a model form, though,
    because we have to add the user info back in after the form is submitted, 
    and handle the possibility of creating new tags, which means we can't just 
    instantiate and go.
    
    """
    
    allcomments = Comment.objects.filter(is_deleted=False).filter(is_parent=True)
    comment_types = CommentType.objects.all()

    comment_type_str = forms.ModelChoiceField(comment_types, \
        label = 'I have a', \
        widget = forms.Select(attrs = {'class' : 'questorcon'}), \
        empty_label = None)
    text = forms.CharField(required=True, label = '', \
        widget=forms.Textarea(attrs= {'class' : 'conquest', }), max_length=300)
    topic = forms.CharField(initial = initial_topic_title, \
        widget=forms.widgets.HiddenInput(attrs = {'class' : 'topic'} ))
    in_reply_to = forms.ModelChoiceField(allcomments, \
        widget = forms.HiddenInput, required=False)
    sources = forms.ModelChoiceField(UserProfile.objects.all(), \
        required = False)
    
    def clean(self):
        """
        make sure we aren't accepting HTML input
        """
        f_value = self.cleaned_data.get('text')
        logger.info("core.forms.CommentSubmitForm(): checking input f_value=%s,"\
            , f_value)
        if f_value == None or f_value.strip() == '':
            logger.error("core.forms.CommentSubmitForm(): comment was empty")
            raise forms.ValidationError('Empty form')
        self.cleaned_data['text'] = utils.sanitize_html(f_value)
        return self.cleaned_data


    class Meta:
        fields = ['comment_type_str', 'text', 'topic', 'in_reply_to', 'sources']
        model = Comment
