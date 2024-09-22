
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from fotopruvodce.core import views as core_views
from fotopruvodce.discussion import views as discussion_views
from fotopruvodce.photos import views as photos_views
from fotopruvodce.registration import views as registration_views
from fotopruvodce.registration.forms import Login as LoginForm
from fotopruvodce.workshops import views as workshops_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', core_views.homepage, name='homepage'),
    path('ucet/set_preference/', core_views.set_preference, name='account-set-preference'),
    path('ucet/profil/', core_views.user_home, name='account-profile'),
    path('ucet/css/', core_views.user_css, name='account-css'),
    path('ucet/fotky/', photos_views.listing_account, name='account-photos-listing'),
    path('ucet/fotky/pridat/', photos_views.add, name='account-photos-add'),
    path('ucet/fotky/upravit/<int:photo_id>/', photos_views.edit, name='account-photos-edit'),
    path('ucet/fotky/smazat/<int:photo_id>/', photos_views.delete, name='account-photos-delete'),

    path('registrace/', registration_views.registration, name="register"),
    path('prihlasit-se/', auth_views.LoginView.as_view(authentication_form=LoginForm), name="login"),
    path('odhlasit-se/', auth_views.LogoutView.as_view(), name="logout"),

    path('fotoforum/', discussion_views.comment_list, {'action': 'time'}, name="comment-time"),
    path('fotoforum/archiv/', discussion_views.comment_list, {'action': 'archive'}, name="comment-archive"),
    re_path(r'^fotoforum/den/(?P<date>\d{3,4}-\d\d-\d\d)/$', discussion_views.comment_list, {'action': 'date'}, name="comment-date"),
    path('fotoforum/temata/', discussion_views.comment_list, {'action': 'themes'}, name="comment-themes"),
    path('fotoforum/uzivatel/', discussion_views.comment_list, {'action': 'user', 'user': ''}, name="comment-user"),
    path('fotoforum/uzivatel/<str:user>/', discussion_views.comment_list, {'action': 'user'}, name="comment-user"),
    path('fotoforum/nove-tema/', discussion_views.comment_add, name="comment-add"),
    path('fotoforum/komentar/<int:obj_id>/', discussion_views.comment_detail, name="comment-detail"),
    path('fotoforum/vlakno/<int:obj_id>/', discussion_views.comment_thread, name="comment-thread"),

    path('fotogalerie/', photos_views.listing, {'action': 'time'}, name="photos-listing-time"),
    re_path(r'^fotogalerie/den/(?P<date>\d{3,4}-\d\d-\d\d)/$', photos_views.listing, {'action': 'date'}, name="photos-listing-date"),
    path('fotogalerie/komentare/', photos_views.comments_listing, {'action': 'time'}, name="photos-listing-comments"),
    path('fotogalerie/komentare/<str:user>/', photos_views.comments_listing, {'action': 'user'}, name="photos-listing-comments-user"),
    path('fotogalerie/mesic/', photos_views.months, name="photos-months"),
    re_path(r'^fotogalerie/mesic/(?P<month>\d{3,4}-\d\d)/$', photos_views.listing, {'action': 'month'}, name="photos-listing-month"),
    path('fotogalerie/sekce/', photos_views.themes, name="photos-sections"),
    path('fotogalerie/sekce/0/', photos_views.listing, {'action': 'section', 'section': None}, name="photos-listing-no-section"),
    path('fotogalerie/sekce/<int:section>/', photos_views.listing, {'action': 'section'}, name="photos-listing-section"),
    path('fotogalerie/skore/', photos_views.total_score_listing, name="photos-listing-score"),
    path('fotogalerie/uzivatel/<str:user>/', photos_views.listing, {'action': 'user'}, name="photos-listing-user"),
    path('fotogalerie/fotka/<int:obj_id>/', photos_views.detail, name="photos-detail"),

    path('workshopy/', workshops_views.listing, name="workshops-listing"),
    path('workshopy/workshop/<int:obj_id>/', workshops_views.detail, name="workshops-detail"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
