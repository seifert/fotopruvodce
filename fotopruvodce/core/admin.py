from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from fotopruvodce.core.models import UserProfile


class UserProfileInline(admin.StackedInline):

    model = UserProfile
    can_delete = False
    readonly_fields = ("email_hash",)


class UserAdmin(BaseUserAdmin):

    readonly_fields = ("first_name", "last_name")
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
