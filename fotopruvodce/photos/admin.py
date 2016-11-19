
from django.contrib import admin

from fotopruvodce.photos.models import Section, Photo, Comment, Rating


admin.site.register(Section)
admin.site.register(Photo)
admin.site.register(Comment)
admin.site.register(Rating)
