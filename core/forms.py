from django import forms
from django.forms.widgets import Select, HiddenInput
from radregator.core.models import Comment,CommentType,Topic
from radregator.tagger.models import Tag
from django.forms.widgets import CheckboxSelectMultiple

class CommentDeleteForm(forms.Form):
    allcomments = Comment.objects.filter(is_deleted=False).filter(is_parent=True)
    comments = forms.ModelMultipleChoiceField(allcomments, )
    
class TopicDeleteForm(forms.Form):
    alltopics = Topic.objects.filter(is_deleted=False)
    topics = forms.ModelMultipleChoiceField(alltopics, )

class NewTopicForm(forms.ModelForm):
    # Comment to source from should default to null
    # Really just using the modelform to validate the title as new
    summary_text = forms.CharField(required = True, widget = forms.TextInput)
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




class CommentSubmitForm(forms.Form):
    """
    Form to let a user submit a comment tied to a particular topic. Note that the topic code requires that at least one topic exist. Using the names
    since those already get accessed in the template; the alternative would be to use a ModelChoiceField with a HiddenInput widget, and make jQuery
    handle changing the topic based on clicking on tabs. It will be possible to simplify this if the UI changes to allow the user to explicitly 
    select a topic or topics (presumably using a ModelMultipleChoiceField).

    Could switch comment_type_str to use a ModelChoiceField on CommentType.objects.all(). 
    It's difficult to make this a model form, though, because we have to add the user info back in after the form is submitted, 
    and handle the possibility of creating new tags, which means we can't just instantiate and go."""
    allcomments = Comment.objects.filter(is_deleted=False).filter(is_parent=True)
    comment_types = CommentType.objects.all()

    comment_type_str = forms.ModelChoiceField(comment_types,label = 'I have a', widget = forms.Select(attrs = {'class' : 'questorcon'}), empty_label = None)
    text = forms.CharField(required=True, label = '', widget=forms.TextInput(attrs= {'class' : 'conquest', }))
    topic = forms.CharField(initial = Topic.objects.all()[0].title, widget=forms.widgets.HiddenInput(attrs = {'class' : 'topic'} ))
    in_reply_to = forms.ModelChoiceField(allcomments, widget = forms.HiddenInput)

    class Meta:
        fields = ['comment_type_str', 'text', 'tags', 'newtag', 'topic', 'in_reply_to']
        model = Comment 
    











