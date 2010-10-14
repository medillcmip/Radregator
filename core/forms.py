from django import forms
from django.forms.widgets import Select
from radregator.core.models import Comment,CommentType,Topic
from radregator.tagger.models import Tag
from django.forms.widgets import CheckboxSelectMultiple

class CommentSubmitForm(forms.ModelForm):
    comment_types = [ct.name for ct in CommentType.objects.all()]

    comment_type = forms.ChoiceField(comment_type.objects.all(), label = 'I have a', widget = forms.Select(attrs = {'class' : 'questorcon'}))
    text = forms.CharField(required=True, label = '', widget=forms.TextInput(attrs= {'class' : 'conquest', }))
    tags = forms.ModelMultipleChoiceField(Tag.objects.all(), widget = CheckboxSelectMultiple(attrs = {'class' : 'tags' }))
    newtag = forms.CharField(initial = "(choose your own)", max_length=80, label = '')
    




    class Meta:
        model = Comment 
        fields = ('comment_type', 'text', 'tags', 'newtag')
    











