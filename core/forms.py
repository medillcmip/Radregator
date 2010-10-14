from django import forms
from django.forms.widgets import Select
from radregator.core.models import Comment,CommentType

class CommentSubmitForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ('text', 'comment_type', 'tags')
        comment_types = [ct.name for ct in CommentType.objects.all()]
        widgets =  {
            'comment_type' : Select(choices = comment_types)}








