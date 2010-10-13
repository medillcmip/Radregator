from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

def index(request):
    """Default view."""
    template_dict = {}

    return render_to_response('index.html', template_dict)

def login(request):
    template_dict = {}
    return render_to_response('login.html',template_dict)
