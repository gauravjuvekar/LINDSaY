from django.conf.urls import patterns, url

from mesg import views, feeds

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),

    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^message/(?P<message_id>\d+)/$', views.message, name='message'),
    url(r'^(?P<division_name>\w+?)/feed/$',
        feeds.DivisionFeed(),
        name='division_feed',
    ),
    url(r'^(?P<division_name>\w+?)/$', views.division, name='division'),
    url(r'^(?P<division_name>\w+?)/(?P<subdivision_name>\w+?)/feed/$',
        feeds.SubDivisionFeed(),
        name='subdivision_feed',
    ),
    url(r'^(?P<division_name>\w+?)/(?P<subdivision_name>\w+?)/$',
        views.subdivision,
        name='subdivision',
    ),
)
