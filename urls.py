from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^newsqa/', include('newsqa.foo.urls')),
    (r'^$', 'radregator.core.views.frontpage'),

    (r'^login', 'radregator.core.views.weblogin'),

    (r'^register', 'radregator.core.views.register'),

    (r'^authenticate', 'radregator.core.views.auth'),

    (r'^api/(?P<output_format>)/topics/(?P<topic_slug>)/comments/(?P<page>\d+)/$', 'radregator.core.views.api_topic_comments'),

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
    print settings.STATIC_DOC_ROOT
