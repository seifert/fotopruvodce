from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, models
from django.urls import reverse
from django.utils.timezone import now

from fotopruvodce.photos.models import Photo


class Workshop(models.Model):

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    active = models.BooleanField(verbose_name="Zobrazit:", default=True, db_index=True)
    timestamp = models.DateTimeField(verbose_name="Založeno:")
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Lektor:",
        related_name="workshops",
        on_delete=models.CASCADE,
    )
    photos = models.ManyToManyField(
        Photo, verbose_name="Fotky:", related_name="workshops"
    )

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return "{} ({}, lektor {})".format(
            self.title, self.timestamp.strftime("%d.%m.%Y"), self.instructor.username
        )

    def get_absolute_url(self):
        return reverse("workshops-detail", args=[self.id])

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=DEFAULT_DB_ALIAS,
        update_fields=None,
    ):
        if self.timestamp is None:
            self.timestamp = now()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
