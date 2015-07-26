from django.conf.urls import patterns, url

from mesg import views, feeds

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/config/$', views.user_config, name='user_config'),
    url(r'^message/create/$', views.create_message, name='create_message'),
    url(r'^message/(?P<message_id>\d+)/expire/$', views.expire_message,
        name='expire_message'),
    url(r'^message/(?P<message_id>\d+)/$', views.message, name='message'),
    url(r'^(?P<category_name>[\w\d_/-]+?)/$', views.category, name='category'),
    url(r'^(?P<category_name>[\w\d_/-]+?)/feed/$', feeds.CategoryFeed(),
        name='category_feed')
)
