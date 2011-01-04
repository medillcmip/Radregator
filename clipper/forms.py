from django import forms
from core import utils

class UrlSubmitForm(forms.Form):
    url_field = forms.URLField(label='Enter the URL of the site you want to clip'\
        , required=True,\
        widget=forms.TextInput(attrs={'size':'70', 'class':'clipper_url_field'}))
    user_comments = forms.CharField(widget=forms.Textarea(\
        attrs={'class':'clipper_text_field', 'col': 52}), required=False, \
        label="Your comments go here: ")

class ClipTextForm(forms.Form):
    """
    want to require selected text so people are encouraged to answer using
    published story
    """
    selected_text = forms.CharField(widget=forms.Textarea(\
        attrs={'cols':32,'class':'clipper_text_field'}), required=True, \
        label="Any text you highlight in the article will appear here!")
    user_comments = forms.CharField(widget=forms.Textarea(\
        attrs={'col':32,'class':'clipper_text_field'}), required=False, \
        label="Add some of your own commentary here.")
    title = forms.CharField(required=False, \
        label="Not the right title for this article?  Mind filling it in for us?"\
        , widget=forms.TextInput(attrs={'size':'30', 'class':'clipper_text_field'}))
    author = forms.CharField(required=False, \
        widget=forms.TextInput(attrs={'class':'clipper_text_field'}),
        label="Is this the person who wrote the article?  " +\
        "No?  Mind putting the right name here?")
    date_published = forms.DateField(required=False, \
        widget=forms.DateTimeInput(format='%m/%d/%Y',attrs={'class':'required date'}),
        label="Does this date look date that this article was " +\
        "published under? If not, could you fix it?")
    url_field = forms.URLField(required=True, widget=forms.HiddenInput)
    comment_id_field = forms.CharField(widget=forms.HiddenInput, required=True)
    topic_id_field = forms.CharField(widget=forms.HiddenInput, required=True)

    def clean(self):
        """
        sanitize user input so there isn't any HTML... issue117
        """
        f_comments = self.cleaned_data.get('user_comments')      
        self.cleaned_data['user_comments'] = utils.sanitize_html(f_comments)
        f_selection = self.cleaned_data.get('selected_text')
        self.cleaned_data['selected_text'] = utils.sanitize_html(f_selection)
        return self.cleaned_data


