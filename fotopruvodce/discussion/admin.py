from django.contrib import admin

from fotopruvodce.discussion.models import AnonymousComment, Comment


class AnonymousCommentInline(admin.TabularInline):

    model = AnonymousComment

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if not obj.is_anonymous:
                return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    inlines = (AnonymousCommentInline,)
    list_display = (
        "id",
        "title",
        "timestamp",
        "user",
        "anonymous_user",
        "parent_raw_id",
        "thread",
    )
    list_display_links = ("id", "title")
    list_select_related = ("user",)
    ordering = ("-timestamp",)
    raw_id_fields = ("user", "parent")
    search_fields = ("title", "user__username", "anonymous__author")

    def anonymous_user(self, obj):
        return obj.anonymous.author

    anonymous_user.short_description = "Anonymous user"

    def parent_raw_id(self, obj):
        return obj.parent.id if obj.parent else None

    parent_raw_id.short_description = "Parent"
