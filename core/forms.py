from django import forms
from django.forms.widgets import Select
from radregator.core.models import Comment,CommentType

class CommentSubmitForm(forms.Form):
    comment_types = [ct.name for ct in CommentType.objects.all()]

    comment_type = forms.ChoiceField(zip(comment_types,comment_types), initial = 'Question', label = 'I have a')
    text = CharField(required=True, label = '')








