from django import forms
from django.forms.widgets import Select
from radregator.core.models import Comment,CommentType,Topic
from radregator.tagger.models import Tag
from django.forms.widgets import CheckboxSelectMultiple

class CommentSubmitForm(forms.ModelForm):
    comment_types = [ct.name for ct in CommentType.objects.all()]

    comment_type = forms.ChoiceField(zip(comment_types,comment_types), initial = 'Question', label = 'I have a')
    text = forms.CharField(required=True, label = '', widget=forms.Textarea)
    tags = forms.ModelMultipleChoiceField(Tag.objects.all(), widget = CheckboxSelectMultiple)
    newtag = forms.CharField(initial = "(choose your own)", max_length=80, label = '')
    




    class Meta:
        model = Comment 
        fields = ('comment_type', 'text', 'tags', 'newtag')
    











