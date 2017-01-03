
from django.contrib import admin

from fotopruvodce.photos.models import Section, Photo, Comment, Rating


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):

    list_display = ('title',)
    ordering = ('title',)


class CommentInline(admin.TabularInline):

    fields = ('content', 'timestamp', 'user')
    model = Comment
    ordering = ('-timestamp',)
    raw_id_fields = ('user',)


class RatingInline(admin.TabularInline):

    fields = ('rating', 'timestamp', 'user')
    model = Rating
    ordering = ('-timestamp',)
    raw_id_fields = ('user',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):

    inlines = (CommentInline, RatingInline,)
    list_display = ('id', 'title', 'timestamp', 'user', 'section', 'active')
    list_display_links = ('id', 'title')
    list_select_related = ('user',)
    ordering = ('-timestamp',)
    raw_id_fields = ('user',)
    search_fields = ('title', 'user__username')
