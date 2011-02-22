from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404 = 'core.views.page_not_found'
urlpatterns = patterns('',
    # Example:
    # (r'^newsqa/', include('newsqa.foo.urls')),
    url(r'^$', 'core.views.frontpage', name="frontpage"),

    url(r'^about/', 'core.views.about_page', name="about"),
    
    url(r'^signup', 'core.views.signup', name="signup"),

    (r'^topic/browse/', 'core.views.browse_topics'),

    (r'^topic/(?P<whichtopic>\d+)/', 'core.views.topic'),

    (r'^reporterview', 'core.views.reporterview'),

    (r'^loginstatus', 'core.views.login_status'),
    
    (r'^login', 'users.views.api_login'),

    (r'^logout', 'users.views.weblogout'),

    #django-registration
    (r'^accounts/register/complete/$',direct_to_template,\
        {'template': 'registration/registration_complete.html'}),
    
    (r'^accounts/register/', 'users.views.register'),
    
    (r'^accounts/', include('registration.urls')),

    (r'^authenticate', 'users.views.auth'),
    
    (r'^clipper_select', 'clipper.views.clipper_submit_select'),

    (r'^clipper/(?P<comment_id>\d+)/(?P<topic_id>\d+/)', 'clipper.views.clipper_paste_url'),


    (r'^clipper_ifrm',direct_to_template,\
        {'template': 'clipper_ifrm.html'}),

    (r'^bootstrapper/(?P<question_id>\d+)/', 'core.views.generate_bootstrapper'),
    
    (r'^api/(?P<output_format>json)/clipper_select/',
     'clipper.views.api_clipper_submit'),

    (r'^deletecomments', 'core.views.deletecomments'),
    (r'^deletetopics', 'core.views.deletetopics'),
    (r'^mergecomments', 'core.views.mergecomments'),
    (r'^newtopic', 'core.views.newtopic'),
    (r'^newsummary', 'core.views.newsummary'),
    (r'^associatecomment', 'core.views.associatecomment'),
    (r'^disassociatecomment', 'core.views.disassociatecomment'),
    (r'^disabled_act', 'users.views.disabled_act'),

    (r'^api/(?P<output_format>json)/topics/(?P<topic_slug_or_id>[\w-]+)/$', \
        'core.views.api_topic'),

    (r'^api/(?P<output_format>json)/topics/$', 'core.views.api_topics'),

    (r'^api/(?P<output_format>json)/topics/(?P<topic_slug_or_id>[\w-]+)/summary/$', \
        'core.views.api_topic_summary'),

    (r'^api/(?P<output_format>json)/topics/(?P<topic_slug_or_id>[\w-]+)/comments/(?P<page>\d+)/$', 'core.views.api_topic_comments'),

    (r'^api/(?P<output_format>json)/comments/(?P<comment_id>\d+)/responses/(?P<response_id>\d*)$',
     'core.views.api_comment_responses'),

    (r'^api/(?P<output_format>json)/users/facebooklogin/$',
     'users.views.api_facebook_auth'),

    (r'^api/(?P<output_format>json)/users/login/$',
     'users.views.api_auth'),

    (r'^api/(?P<output_format>json)/users/$',
     'users.views.api_users'),

    (r'^api/(?P<output_format>json)/comments/$',
     'core.views.api_commentsubmission'),

    (r'^api/(?P<output_format>json)/comments/tag/$',
     'core.views.api_comment_tag'),

    (r'^api/(?P<output_format>json)/topics/tag/$',
     'core.views.api_topic_tag'),

    (r'^api/(?P<output_format>json)/comments/submit',
     'core.views.api_commentsubmission'),

    (r'^commentsubmit',
     'core.views.api_commentsubmission'), # For debugging purposes

    (r'^api/(?P<output_format>json)/questions/$', \
     'core.views.api_questions'),

    (r'^api/(?P<output_format>json)/invite/$', \
     'users.views.api_invite'),

    # Some testing forms for new features
    (r'^simpletest/(?P<whichtest>\w+)', 'core.views.simpletest'),

    (r'^api/(?P<output_format>json)/invite/$', \
     'users.views.api_invite')
)

# Add the admin stuff
urlpatterns += patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# Serve static content.  This is inneficient and insecure
# but we'll use this for development.
# See http://docs.djangoproject.com/en/dev/howto/static-files/
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT}),
    )
