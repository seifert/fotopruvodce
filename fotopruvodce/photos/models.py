
import datetime
import os.path

from django.conf import settings
from django.db import models, DEFAULT_DB_ALIAS
from django.urls import reverse
from django.utils.timezone import now


class Section(models.Model):

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


def upload_photo_fullpath(instance, filename):
    timestamp = instance.timestamp or datetime.datetime.now()
    return os.path.join(timestamp.strftime('photos/%Y/%m/%d/'), filename)


class Photo(models.Model):

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='photos')
    section = models.ForeignKey(Section, related_name='photos')
    thumbnail_height = models.PositiveIntegerField()
    thumbnail_width = models.PositiveIntegerField()
    thumbnail = models.ImageField(
        upload_to=upload_photo_fullpath, height_field='thumbnail_height',
        width_field='thumbnail_width')
    photo_height = models.PositiveIntegerField()
    photo_width = models.PositiveIntegerField()
    photo = models.ImageField(
        upload_to=upload_photo_fullpath, height_field='photo_height',
        width_field='photo_width')
    _thumbnail_url = models.CharField(max_length=128, blank=True)
    _photo_url = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('photos-detail', args=[self.id])

    def save(self, force_insert=False, force_update=False,
             using=DEFAULT_DB_ALIAS, update_fields=None):
        if self.timestamp is None:
            self.timestamp = now()
        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)


class Comment(models.Model):

    content = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    photo = models.ForeignKey(Photo, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='photos_comments')

    def save(self, force_insert=False, force_update=False,
             using=DEFAULT_DB_ALIAS, update_fields=None):
        if self.timestamp is None:
            self.timestamp = now()
        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)

    def __str__(self):
        return "Photo {} '{}': '{}'".format(
            self.photo.id, self.photo.title[:50], self.content[:50]
        )


class Rating(models.Model):

    rating = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField()
    photo = models.ForeignKey(Photo, related_name='ratings')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='photos_ratings')

    def save(self, force_insert=False, force_update=False,
             using=DEFAULT_DB_ALIAS, update_fields=None):
        if self.timestamp is None:
            self.timestamp = now()
        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)

    def __str__(self):
        return "Photo {} '{}': {}".format(
            self.photo.id, self.photo.title[:50], self.rating
        )
