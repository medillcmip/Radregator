from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from fbapi.facebook import *
from models import Topic
from radregator.core.forms import CommentSubmitForm

def frontpage(request):
    """ Front page demo"""

    if request.method == 'POST':
        pass

    template_dict = {}

    topics = Topics.objects.all()[:5] # Will want to filter, order in later versions

    template_dict['topics'] = topics
    template_dict['comment_form'] = CommentSubmitForm()

    return render_to_response('frontpage.html', template_dict)




    
    return render_to_response('frontpage.html', template_dict)
def index(request):
    """Default view."""
    template_dict = {}

    return render_to_response('index.html', template_dict)

def login(request):
    template_dict = {}
    template_dict['fb_app_id']=settings.FB_API_ID
    user = get_user_from_cookie(request.COOKIES, settings.FB_API_ID,settings.FB_SECRET_KEY )
    if user:
        graph = GraphAPI(user["access_token"])
        profile = graph.get_object("me")
        friends = graph.get_connections("me", "friends")
        template_dict['fb_friends'] = friends['data']
    return render_to_response('login.html',template_dict)
