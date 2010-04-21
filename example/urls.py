import os.path

from django.conf.urls.defaults import *
from django.conf import settings

import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^harness/', include('harness.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    url(r'email/(?P<email>.*)$', views.email, name='email_view'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT,
                 'show_indexes': True}),
        )
