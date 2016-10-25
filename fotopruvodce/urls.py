
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from fotopruvodce.core import views as core_views
from fotopruvodce.registration import views as registration_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url('^registrace/$', registration_views.registration, name="register"),
    url('^prihlasit-se/$', auth_views.login, name="login"),
    url('^odhlasit-se/$', auth_views.logout, name="logout"),

    url(r'^$', core_views.homepage, name='homepage'),
]
