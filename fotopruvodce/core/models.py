import hashlib
import inspect
import json
import random
import string

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save

from fotopruvodce.core.logging import logger
from fotopruvodce.core.text import MARKDOWN_HELP_TEXT

SALT_CHARS = string.ascii_letters + string.digits


def hash_email(email, alg="sha256", salt=None):
    if not email:
        raise ValueError("E-mail is empty")
    if salt is None:
        salt = "".join(random.sample(SALT_CHARS, 4))
    h = hashlib.new(alg)
    h.update(bytes(salt, "ascii"))
    h.update(bytes(email.lower(), "utf-8"))
    return "{}:{}:{}".format(alg, salt, h.hexdigest())


class Preferences(object):

    DEFAULT_HP_BOXES = [
        "new-photos-box",
        "new-photos-comments-box",
        "new-discussion-comments-box",
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
                    i[0] for i in inspect.getmembers(cls) if isinstance(i[1], property)
                }
                for k, v in data.items():
                    if k in preferences_names:
                        setattr(inst, k, v)
                    else:
                        logger.warning("%s: unknown preference '%s'", cls.__name__, k)
            except Exception:
                logger.exception("%s: invalid value %r", cls.__name__, data)

        return inst

    def to_json(self):
        return json.dumps(self._data, indent=4, sort_keys=True)

    @property
    def hp_boxes(self):
        return self._data.get("hp_boxes", self.DEFAULT_HP_BOXES)

    @hp_boxes.setter
    def hp_boxes(self, data):
        if isinstance(data, list):
            try:
                all_items_set = set(self.DEFAULT_HP_BOXES)
                items = [i for i in data if i in all_items_set]
                items.extend(i for i in self.DEFAULT_HP_BOXES if i not in items)
                self._data["hp_boxes"] = items
            except Exception:
                pass


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    description = models.TextField(blank=True, help_text=MARKDOWN_HELP_TEXT)
    old_password = models.CharField(max_length=16, blank=True)
    preferences_json = models.TextField(verbose_name="Konfigurace", blank=True)
    custom_css = models.TextField(verbose_name="CSS", blank=True)
    email_hash = models.CharField(max_length=256, blank=True)

    @classmethod
    def clear_gdpr_fields(cls, sender, instance, **kwargs):
        if instance.email:
            instance._email = instance.email
        instance.email = ""
        instance.first_name = ""
        instance.last_name = ""

    @classmethod
    def create_or_update_profile(cls, sender, instance, created, **kwargs):
        if hasattr(instance, "_email"):
            email_hash = hash_email(instance._email)
            delattr(instance, "_email")
        else:
            email_hash = ""
        if created:
            profile = cls(user=instance, email_hash=email_hash)
            profile.save()
        else:
            if email_hash:
                instance.profile.email_hash = email_hash
                instance.profile.save()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.preferences:
            self.preferences_json = self.preferences.to_json()
        else:
            self.preferences_json = ""
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    @property
    def preferences(self):
        if not hasattr(self, "_preferences"):
            self._preferences = Preferences.from_json(self.preferences_json)
        return self._preferences


pre_save.connect(UserProfile.clear_gdpr_fields, sender=User)
post_save.connect(UserProfile.create_or_update_profile, sender=User)
