
from django.conf import settings
from django.db import models, DEFAULT_DB_ALIAS
from django.urls import reverse
from django.utils.timezone import now


class Comment(models.Model):

    title = models.CharField(max_length=128, blank=False)
    content = models.TextField(blank=False)
    timestamp = models.DateTimeField(blank=False, null=False)
    ip = models.GenericIPAddressField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    parent = models.ForeignKey('self', blank=True, null=True)
    thread = models.IntegerField(blank=False, null=False, default=0, db_index=True)
    level = models.IntegerField(blank=False, null=False, default=0, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('comment-detail', args=[self.id])

    def save(self, force_insert=False, force_update=False,
             using=DEFAULT_DB_ALIAS, update_fields=None):
        if self.timestamp is None:
            self.timestamp = now()
        # Reply - inherit thread id from parent and increase level
        if self.thread == 0 and self.parent:
            self.thread = self.parent.thread
            self.level = self.parent.level + 1
        # Save
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        # New thread - inherit thread id from pk and save again
        if self.thread == 0:
            self.thread = self.pk
            super().save(force_insert=False, force_update=True,
                         using=using, update_fields=['thread'])

class AnonymousComment(models.Model):

    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='anonymous')
    author = models.CharField(max_length=25)
    email = models.CharField(max_length=64, blank=True)
