
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    description = models.TextField(blank=True)
    displayed_email = models.CharField(max_length=128, blank=True)
    old_password = models.CharField(max_length=16, blank=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
