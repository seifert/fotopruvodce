
from django.conf import settings
from django.db import models, DEFAULT_DB_ALIAS
from django.utils.timezone import now


TODO_STATUS = (
    (1, "Nový"),
    (2, "Akceptováno"),
    (3, "Zavřeno"),
)


class Ticket(models.Model):

    title = models.CharField(
        verbose_name="Název:", max_length=128)
    description = models.TextField(
        verbose_name="Popis:", blank=True)
    timestamp = models.DateTimeField(
        verbose_name="Vloženo:")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Uživatel:",
        related_name='todo')
    status = models.IntegerField(
        verbose_name="Stav:", choices=TODO_STATUS, default=1)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False,
             using=DEFAULT_DB_ALIAS, update_fields=None):
        if self.timestamp is None:
            self.timestamp = now()
        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)


class Comment(models.Model):

    content = models.TextField(blank=False)
    timestamp = models.DateTimeField()
    ticket = models.ForeignKey(Ticket, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='ticket_comments')

    class Meta:
        ordering = ('timestamp',)

    def save(self, force_insert=False, force_update=False,
             using=DEFAULT_DB_ALIAS, update_fields=None):
        if self.timestamp is None:
            self.timestamp = now()
        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
