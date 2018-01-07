
import io
import os.path

from PIL import Image

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, DEFAULT_DB_ALIAS
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

from fotopruvodce.core.text import MARKDOWN_HELP_TEXT


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
    timestamp = instance.timestamp or now()
    extension = os.path.splitext(filename)[1]
    filename = "{}-{}".format(instance.user.username, slugify(instance.title))
    if thumbnail:
        filename = filename + '-thumb'
    if extension:
        filename = filename + extension
    return os.path.join(timestamp.strftime('photos/%Y/%m/%d/'), filename)


def upload_thumb_fullpath(instance, filename):
    return upload_photo_fullpath(instance, filename, thumbnail=True)


def upload_series_photo_fullpath(instance, filename):
    timestamp = instance.photo.timestamp
    extension = os.path.splitext(filename)[1]
    filename = "{}-{}".format(
        instance.photo.user.username, slugify(instance.photo.title))
    if extension:
        filename = filename + extension
    return os.path.join(timestamp.strftime('photos/%Y/%m/%d/'), filename)


def validate_thumbnail(value):
    if (
        not value.instance.id and (
            value.size > settings.THUMB_MAX_UPLOAD_SIZE or
            value.width > settings.THUMB_MAX_SIZE[0] or
            value.height > settings.THUMB_MAX_SIZE[1])
    ):
        raise ValidationError('Překročena povolená velikost náhledu')


def validate_photo(value):
    if (
        not value.instance.id and (
            value.size > settings.PHOTO_MAX_UPLOAD_SIZE or
            value.width > settings.PHOTO_MAX_SIZE[0] or
            value.height > settings.PHOTO_MAX_SIZE[1])
    ):
        raise ValidationError('Překročena povolená velikost fotky')


class Photo(models.Model):

    title = models.CharField(
        verbose_name="Název fotky", max_length=128)
    description = models.TextField(
        verbose_name="Popis", blank=True, help_text=MARKDOWN_HELP_TEXT)
    active = models.BooleanField(
        verbose_name="Zobrazit v galerii", default=True, db_index=True)
    deleted = models.BooleanField(
        verbose_name="Smazáno", default=False, db_index=True)
    timestamp = models.DateTimeField(
        verbose_name="Vloženo")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Autor",
        related_name='photos')
    section = models.ForeignKey(
        Section, related_name='photos', verbose_name="Sekce",
        null=True, blank=True)
    thumbnail_height = models.PositiveIntegerField(
        verbose_name="Výška náhledu")
    thumbnail_width = models.PositiveIntegerField(
        verbose_name="Šířka náhledu")
    thumbnail = models.ImageField(
        verbose_name="Náhled", upload_to=upload_thumb_fullpath,
        height_field='thumbnail_height', width_field='thumbnail_width',
        validators=[validate_thumbnail])
    photo_height = models.PositiveIntegerField(
        verbose_name="Výška fotky")
    photo_width = models.PositiveIntegerField(
        verbose_name="Šířka fotky")
    photo = models.ImageField(
        verbose_name="Fotka", upload_to=upload_photo_fullpath,
        height_field='photo_height', width_field='photo_width',
        validators=[validate_photo])
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
        if self.deleted is True and self.active:
            self.active = False
        if self.photo != 'noimage.gif' and self.thumbnail == 'noimage.gif':
            self.thumbnail = ''
        if not self.thumbnail:
            self.generate_thumbnail()
        if self._photo_url and self.photo != 'noimage.gif':
            self._photo_url = ''
        if self._thumbnail_url and self.thumbnail != 'noimage.gif':
            self._thumbnail_url = ''

        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)

    def generate_thumbnail(self):
        thumbnail_content = io.BytesIO()

        img = Image.open(self.photo)
        img.thumbnail(settings.THUMB_DEFAULT_SIZE, Image.BICUBIC)
        img.save(thumbnail_content, img.format)

        filename = upload_photo_fullpath(self, self.photo.name, thumbnail=True)
        self.thumbnail.save(filename, thumbnail_content, save=False)

    @property
    def rating_stats(self):
        return self.ratings.aggregate(
            count=models.Count('*'),
            sum=models.Sum('rating'),
            avg=models.Avg('rating'),
        )

    @property
    def photos(self):
        return [self.photo] + [sp.image for sp in self.series_photos.all()]


class SeriesPhoto(models.Model):

    photo = models.ForeignKey(Photo, related_name='series_photos')
    height = models.PositiveIntegerField(verbose_name="Výška")
    width = models.PositiveIntegerField(verbose_name="Šířka")
    image = models.ImageField(
        verbose_name="Fotka", upload_to=upload_series_photo_fullpath,
        height_field='height', width_field='width',
        validators=[validate_photo])

    class Meta:
        ordering = ['id']

    def __repr__(self):
        return "<{}: {} #{}>".format(
            self.__class__.__name__, self.photo.title, self.id)


class Comment(models.Model):

    content = models.TextField(blank=True, help_text=MARKDOWN_HELP_TEXT)
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
