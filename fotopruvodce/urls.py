
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from fotopruvodce.core import views as core_views
from fotopruvodce.discussion import views as discussion_views
from fotopruvodce.photos import views as photos_views
from fotopruvodce.registration import views as registration_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', core_views.homepage, name='homepage'),
    url(r'^osobni-stranka/$', core_views.user_home, name='user-home'),

    url(r'^registrace/$', registration_views.registration, name="register"),
    url(r'^prihlasit-se/$', auth_views.login, name="login"),
    url(r'^odhlasit-se/$', auth_views.logout, name="logout"),

    url(r'^fotoforum/$', discussion_views.comment_list, {'action': 'time'}, name="comment-time"),
    url(r'^fotoforum/archiv/$', discussion_views.comment_list, {'action': 'archive'}, name="comment-archive"),
    url(r'^fotoforum/den/(?P<date>\d{3,4}-\d\d-\d\d)/$', discussion_views.comment_list, {'action': 'date'}, name="comment-date"),
    url(r'^fotoforum/temata/$', discussion_views.comment_list, {'action': 'themes'}, name="comment-themes"),
    url(r'^fotoforum/uzivatel/$', discussion_views.comment_list, {'action': 'user', 'user': ''}, name="comment-user"),
    url(r'^fotoforum/uzivatel/(?P<user>.+)/$', discussion_views.comment_list, {'action': 'user'}, name="comment-user"),
    url(r'^fotoforum/nove-tema/$', discussion_views.comment_add, name="comment-add"),
    url(r'^fotoforum/komentar/([0-9]+)/$', discussion_views.comment_detail, name="comment-detail"),
    url(r'^fotoforum/vlakno/([0-9]+)/$', discussion_views.comment_thread, name="comment-thread"),

    url(r'^fotogalerie/$', photos_views.listing, {'action': 'time'}, name="photos-listing-time"),
    url(r'^fotogalerie/uzivatel/(?P<user>.+)/$', photos_views.listing, {'action': 'user'}, name="photos-listing-user"),
    url(r'^fotogalerie/fotka/([0-9]+)/$', photos_views.detail, name="photos-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
