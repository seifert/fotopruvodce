
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Comment(models.Model):

    title = models.CharField(max_length=128, blank=False)
    content = models.TextField(blank=False)
    timestamp = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    ip = models.GenericIPAddressField(blank=False)
    user = models.ForeignKey(User, blank=False, null=False)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('comment-detail', args=[self.id])
