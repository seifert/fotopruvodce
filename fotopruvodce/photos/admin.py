from django.contrib import admin

from fotopruvodce.photos.models import Comment, Photo, Rating, Section, SeriesPhoto
from fotopruvodce.workshops.models import Workshop


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):

    list_display = ("title",)
    ordering = ("title",)


class WorkshopPhotosInline(admin.TabularInline):

    model = Workshop.photos.through


class SeriesPhotoInline(admin.TabularInline):

    fields = ("image",)
    model = SeriesPhoto
    extra = 2
    max_num = 2


class CommentInline(admin.TabularInline):

    fields = ("content", "timestamp", "user")
    model = Comment
    ordering = ("-timestamp",)
    raw_id_fields = ("user",)


class RatingInline(admin.TabularInline):

    fields = ("rating", "timestamp", "user")
    model = Rating
    ordering = ("-timestamp",)
    raw_id_fields = ("user",)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):

    inlines = (
        WorkshopPhotosInline,
        SeriesPhotoInline,
        CommentInline,
        RatingInline,
    )
    list_display = ("id", "title", "timestamp", "user", "section", "active")
    list_display_links = ("id", "title")
    list_select_related = ("user",)
    ordering = ("-timestamp",)
    raw_id_fields = ("user",)
    search_fields = ("title", "user__username")
