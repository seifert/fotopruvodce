
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from fotopruvodce.core.text import MARKDOWN_HELP_TEXT


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    description = models.TextField(blank=True, help_text=MARKDOWN_HELP_TEXT)
    displayed_email = models.CharField(max_length=128, blank=True)
    old_password = models.CharField(max_length=16, blank=True)

    @classmethod
    def create_user_profile(cls, sender, instance, created, **kwargs):
        if created:
            profile, created = cls.objects.get_or_create(user=instance)

post_save.connect(UserProfile.create_user_profile, sender=User)
