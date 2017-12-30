
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from fotopruvodce.core import views as core_views
from fotopruvodce.discussion import views as discussion_views
from fotopruvodce.photos import views as photos_views
from fotopruvodce.registration import views as registration_views
from fotopruvodce.workshops import views as workshops_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', core_views.homepage, name='homepage'),
    url(r'^ucet/set_preference/$', core_views.set_preference, name='account-set-preference'),
    url(r'^ucet/osobni-udaje/$', core_views.user_home, name='account-personal-info'),
    url(r'^ucet/fotky/$', photos_views.listing_account, name='account-photos-listing'),
    url(r'^ucet/fotky/pridat/$', photos_views.add, name='account-photos-add'),
    url(r'^ucet/fotky/upravit/([0-9]+)/$', photos_views.edit, name='account-photos-edit'),
    url(r'^ucet/fotky/smazat/([0-9]+)/$', photos_views.delete, name='account-photos-delete'),

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
    url(r'^fotogalerie/den/(?P<date>\d{3,4}-\d\d-\d\d)/$', photos_views.listing, {'action': 'date'}, name="photos-listing-date"),
    url(r'^fotogalerie/komentare/$', photos_views.comments_listing, {'action': 'time'}, name="photos-listing-comments"),
    url(r'^fotogalerie/komentare/(?P<user>.+)/$', photos_views.comments_listing, {'action': 'user'}, name="photos-listing-comments-user"),
    url(r'^fotogalerie/mesic/$', photos_views.months, name="photos-months"),
    url(r'^fotogalerie/mesic/(?P<month>\d{3,4}-\d\d)/$', photos_views.listing, {'action': 'month'}, name="photos-listing-month"),
    url(r'^fotogalerie/sekce/$', photos_views.themes, name="photos-sections"),
    url(r'^fotogalerie/sekce/0/$', photos_views.listing, {'action': 'section', 'section': None}, name="photos-listing-no-section"),
    url(r'^fotogalerie/sekce/(?P<section>\d+)/$', photos_views.listing, {'action': 'section'}, name="photos-listing-section"),
    url(r'^fotogalerie/skore/$', photos_views.total_score_listing, name="photos-listing-score"),
    url(r'^fotogalerie/uzivatel/(?P<user>.+)/$', photos_views.listing, {'action': 'user'}, name="photos-listing-user"),
    url(r'^fotogalerie/fotka/([0-9]+)/$', photos_views.detail, name="photos-detail"),

    url(r'^workshopy/$', workshops_views.listing, name="workshops-listing"),
    url(r'^workshopy/workshop/([0-9]+)/$', workshops_views.detail, name="workshops-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
