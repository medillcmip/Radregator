from django import forms

class UrlSubmitForm(forms.Form):
    urlfield = forms.URLField(label='Site you want to clip', required=True)

class ClipTextForm(forms.Form):
    #TODO: enlarge via CSS
    selected_text = forms.CharField(widget=forms.Textarea, required=True)
    urlfield = forms.URLField(required=True, widget=forms.HiddenInput)

