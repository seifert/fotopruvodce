
import inspect
import json

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from fotopruvodce.core.logging import logger
from fotopruvodce.core.text import MARKDOWN_HELP_TEXT


class Preferences(object):

    DEFAULT_HP_BOXES = [
        'new-photos-box',
        'new-photos-comments-box',
        'new-discussion-comments-box'
    ]

    def __init__(self):
        self._data = {}

    def __str__(self):
        return str(self._data)

    def __bool__(self):
        return bool(self._data)

    @classmethod
    def from_json(cls, data):
        inst = cls()

        if data:
            try:
                data = json.loads(data)
                preferences_names = {
                    i[0] for i in inspect.getmembers(cls)
                    if isinstance(i[1], property)
                }
                for k, v in data.items():
                    if k in preferences_names:
                        setattr(inst, k, v)
                    else:
                        logger.warning(
                            "%s: unknown preference '%s'", cls.__name__, k)
            except Exception:
                logger.exception("%s: invalid value %r", cls.__name__, data)

        return inst

    def to_json(self):
        return json.dumps(self._data, indent=4, sort_keys=True)

    @property
    def hp_boxes(self):
        return self._data.get('hp_boxes', self.DEFAULT_HP_BOXES)

    @hp_boxes.setter
    def hp_boxes(self, data):
        if isinstance(data, list):
            try:
                all_items_set = set(self.DEFAULT_HP_BOXES)
                items = [i for i in data if i in all_items_set]
                items.extend(i for i in self.DEFAULT_HP_BOXES if i not in items)
                self._data['hp_boxes'] = items
            except Exception:
                pass


class UserProfile(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    description = models.TextField(blank=True, help_text=MARKDOWN_HELP_TEXT)
    displayed_email = models.CharField(max_length=128, blank=True)
    old_password = models.CharField(max_length=16, blank=True)
    preferences_json = models.TextField(verbose_name="Konfigurace", blank=True)

    @classmethod
    def create_user_profile(cls, sender, instance, created, **kwargs):
        if created:
            unused_profile, created = cls.objects.get_or_create(user=instance)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.preferences:
            self.preferences_json = self.preferences.to_json()
        else:
            self.preferences_json = ''
        return super().save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields)

    @property
    def preferences(self):
        if not hasattr(self, '_preferences'):
            self._preferences = Preferences.from_json(self.preferences_json)
        return self._preferences


post_save.connect(UserProfile.create_user_profile, sender=User)
