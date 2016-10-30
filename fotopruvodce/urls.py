
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from fotopruvodce.core import views as core_views
from fotopruvodce.discussion import views as discussion_views
from fotopruvodce.registration import views as registration_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', core_views.homepage, name='homepage'),
    url(r'^osobni-stranka/$', core_views.user_home, name='user-home'),

    url('^registrace/$', registration_views.registration, name="register"),
    url('^prihlasit-se/$', auth_views.login, name="login"),
    url('^odhlasit-se/$', auth_views.logout, name="logout"),

    url('^fotoforum/$', discussion_views.comment_list, name="comment-list"),
    url('^fotoforum/komentar/novy/$', discussion_views.comment_add, name="comment-add"),
    url('^fotoforum/komentar/([0-9]+)/$', discussion_views.comment_detail, name="comment-detail"),
]
