
import datetime
import os.path

from django.conf import settings
from django.db import models, DEFAULT_DB_ALIAS
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now


class Section(models.Model):

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('photos-listing-section', args=[self.id])


def upload_photo_fullpath(instance, filename, thumbnail=False):
    timestamp = instance.timestamp or datetime.datetime.now()
    extension = os.path.splitext(filename)[1]
    filename = "{}-{}".format(instance.user.username, slugify(instance.title))
    if thumbnail:
        filename = filename + '-thumb'
    if extension:
        filename = filename + extension
    return os.path.join(timestamp.strftime('photos/%Y/%m/%d/'), filename)


def upload_thumb_fullpath(instance, filename):
    return upload_photo_fullpath(instance, filename, thumbnail=True)


class Photo(models.Model):

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='photos')
    section = models.ForeignKey(
        Section, related_name='photos', null=True, blank=True)
    thumbnail_height = models.PositiveIntegerField()
    thumbnail_width = models.PositiveIntegerField()
    thumbnail = models.ImageField(
        upload_to=upload_thumb_fullpath, height_field='thumbnail_height',
        width_field='thumbnail_width')
    photo_height = models.PositiveIntegerField()
    photo_width = models.PositiveIntegerField()
    photo = models.ImageField(
        upload_to=upload_photo_fullpath, height_field='photo_height',
        width_field='photo_width')
    _thumbnail_url = models.CharField(max_length=128, blank=True)
    _photo_url = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['-timestamp']

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

    @property
    def rating_stats(self):
        return self.ratings.aggregate(
            count=models.Count('*'),
            sum=models.Sum('rating'),
            avg=models.Avg('rating'),
        )


class Comment(models.Model):

    content = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    photo = models.ForeignKey(Photo, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='photos_comments')

    class Meta:
        ordering = ('timestamp',)

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

    class Meta:
        unique_together = (('photo', 'user'),)
        ordering = ('timestamp',)

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
