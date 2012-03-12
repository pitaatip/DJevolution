from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.list import ListView
from nonrelblog.models import Post

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

post_list = ListView.as_view(model=Post, template_name='post_list.html')

urlpatterns = patterns('',
    url(r'^pita_django/post/(?P<pk>[a-z\d]+)/$', 'nonrelblog.views.post_detail', name='post_detail'),
    url(r'^pita_django/delete_post/(?P<pk>[a-z\d]+)/$', 'nonrelblog.views.post_delete', name='post_delete'),
    url(r'^pita_django/$', post_list, name='post_list'),
    url(r'^pita_django/addPost/$', 'nonrelblog.views.addPost'),
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
)
