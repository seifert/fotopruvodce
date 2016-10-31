
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

    @property
    def children(self):
        """
        Children of the this comment.
        """
        return Comment.objects.filter(parent=self).order_by('timestamp')

    def get_main_comment(self, _comment=None):
        """
        Return main (first) comment for discussion thread identified by
        this comment.
        """
        if _comment is None:
            _comment = self

        if _comment.parent is None:
            return _comment
        else:
            return self.get_main_comment(_comment.parent)

    def get_tree(self, _comment=None, _tree=None, _level=0):
        """
        Return tree of the comments for discussion thread identified by
        this comment.
        """
        if _comment is None:
            _comment = self.get_main_comment(self)
        if _tree is None:
            _tree = []

        _tree.append((_comment, _level))

        _level += 1
        for child in _comment.children:
            self.get_tree(child, _tree, _level)

        return _tree
