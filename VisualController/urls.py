from django.conf.urls.defaults import patterns, include, url
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from VisualControllerApp.models import Computation, ActualConfig


admin.autodiscover()

computation_list = ListView.as_view(model=Computation, template_name='computation/list.html')

urlpatterns = patterns('',
    url(r'^VisualControllerApp/comp/(?P<pk>[a-z\d]+)/$', 'VisualControllerApp.views.comp_detail', name='comp_detail'),
    url(r'^VisualControllerApp/order/computation/$', 'VisualControllerApp.views.orderComputation'),
    url(r'^VisualControllerApp/order/configuration/$', 'VisualControllerApp.views.set_configuration'),
    url(r'^VisualControllerApp/(?P<view_name>[a-z/]+)/$', 'VisualControllerApp.views.simple_render'),
    url(r'^VisualControllerApp/$', computation_list, name='computation_list'),
    url(r'^VisualControllerApp/order/start$', 'VisualControllerApp.views.start_computation'),
    url(r'^VisualControllerApp/delete_comp/(?P<pk>[a-z\d]+)/$', 'VisualControllerApp.views.comp_delete', name='comp_delete'),

    # Examples:
    # url(r'^$', 'VisualController.views.home', name='home'),
    # url(r'^VisualController/', include('VisualController.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()