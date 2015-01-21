from django.conf.urls import patterns, include, url
from django.contrib import admin
from common import urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'journeytech.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'common.views.home_view.main', name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/', include(urls)),
)
