from django import forms
from django.forms.widgets import Select
from radregator.core.models import Comment,CommentType,Topic
from radregator.tagger.models import Tag
from django.forms.widgets import CheckboxSelectMultiple

class CommentSubmitForm(forms.Form):
    comment_types = [ct.name for ct in CommentType.objects.all()]

    comment_type_str = forms.ChoiceField(zip(comment_types,comment_types), label = 'I have a', widget = forms.Select(attrs = {'class' : 'questorcon'}))
    text = forms.CharField(required=True, label = '', widget=forms.TextInput(attrs= {'class' : 'conquest', }))
    tags = forms.ModelMultipleChoiceField(Tag.objects.all(), widget = CheckboxSelectMultiple(attrs = {'class' : 'tags' }))
    newtag = forms.CharField(initial = "", max_length=80, label = '', required=False)
    topic = forms.CharField(initial = Topic.objects.all()[0].title, widget=forms.widgets.HiddenInput(attrs = {'class' : 'topic'} ))
    




    class Meta:
        fields = ['comment_type_str', 'text', 'tags', 'newtag', 'topic']
        model = Comment 
    











