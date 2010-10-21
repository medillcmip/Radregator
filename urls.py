from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^newsqa/', include('newsqa.foo.urls')),
    (r'^$', 'radregator.core.views.frontpage'),

    (r'^reporterview', 'radregator.core.views.reporterview'),

    (r'^login', 'radregator.users.views.weblogin'),

    (r'^logout', 'radregator.users.views.weblogout'),

    (r'^register', 'radregator.users.views.register'),

    (r'^authenticate', 'radregator.users.views.auth'),
    
    (r'^accounts/login/$', 'radregator.users.views.weblogin'),

    (r'^accounts/login/register/$', 'radregator.users.views.register'),
    
    (r'^clipper_select', 'radregator.clipper.views.clipper_submit_select'),
    
    (r'^clipper', 'radregator.clipper.views.clipper_paste_url'),

    (r'^deletecomments', 'radregator.core.views.deletecomments'),
    (r'^deletetopics', 'radregator.core.views.deletetopics'),
    (r'^mergecomments', 'radregator.core.views.mergecomments'),
    (r'^newtopic', 'radregator.core.views.newtopic'),
    (r'^associatecomment', 'radregator.core.views.associatecomment'),
    (r'^disassociatecomment', 'radregator.core.views.disassociatecomment'),
    (r'^disabled_act', 'radregator.users.views.disabled_act'),

    (r'^api/(?P<output_format>json)/topics/(?P<topic_slug_or_id>[\w-]+)/comments/(?P<page>\d+)/$', 'radregator.core.views.api_topic_comments'),

    (r'^api/(?P<output_format>json)/comments/(?P<comment_id>\d+)/responses/(?P<response_id>\d*)$',
     'radregator.core.views.api_comment_responses'),

    (r'^api/(?P<output_format>json)/users/(?P<uri_username>[a-zA-Z]\w+)/login/$',
     'radregator.users.views.api_auth'),

    (r'^api/(?P<output_format>json)/users/$',
     'radregator.users.views.api_users'),

    (r'^api/(?P<output_format>json)/comments/submit',
     'radregator.core.views.api_commentsubmission'),

    (r'^commentsubmit',
     'radregator.core.views.api_commentsubmission'), # For debugging purposes

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Some testing forms for new features
    (r'^simpletest/(?P<whichtest>\w+)', 'radregator.core.views.simpletest'),
)

# Serve static content.  This is inneficient and insecure
# but we'll use this for development.
# See http://docs.djangoproject.com/en/dev/howto/static-files/
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT}),
    )
    print settings.STATIC_DOC_ROOT
