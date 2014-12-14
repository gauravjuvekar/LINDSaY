from django.conf.urls import patterns, url

from mesg import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<division_name>.+)/$', views.division, name='division'),
    url(r'^(?P<division_name>.+)/(?P<subdivision_name>.+)$', views.subdivision,name='subdivision'),
)
