from django.contrib import admin

from fotopruvodce.todo.models import Comment, Ticket


class CommentInline(admin.TabularInline):

    can_delete = False
    fields = ("content", "timestamp", "user")
    model = Comment
    ordering = ("-timestamp",)
    raw_id_fields = ("user",)
    readonly_fields = ("timestamp", "user")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    actions_on_top = False
    actions_on_bottom = False
    inlines = (CommentInline,)
    list_display = ("id", "title", "user", "timestamp", "status")
    list_display_links = ("id", "title")
    list_filter = ("status",)
    list_select_related = ("user",)
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp", "user")
    search_fields = ("title", "user__username")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Comment):
                if not instance.user_id:
                    instance.user = request.user
                instance.save()
