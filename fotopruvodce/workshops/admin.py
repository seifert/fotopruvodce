
from django.contrib import admin

from fotopruvodce.workshops.models import Workshop


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):

    exclude = ('photos',)
    list_display = ('id', 'title', 'timestamp', 'instructor', 'active')
    list_display_links = ('id', 'title')
    list_select_related = ('instructor',)
    ordering = ('-timestamp',)
    raw_id_fields = ('instructor',)
    search_fields = ('title', 'instructor__username')
