from django import forms

class UrlSubmitForm(forms.Form):
    url_field = forms.URLField(label='Site you want to clip', required=True)

class ClipTextForm(forms.Form):
    #TODO: enlarge via CSS
    selected_text = forms.CharField(widget=forms.Textarea, required=True)
    url_field = forms.URLField(required=True, widget=forms.HiddenInput)
    comment_id_field = forms.CharField(widget=forms.HiddenInput, required=True)
