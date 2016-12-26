
from django.template import Library

from fotopruvodce.discussion.models import Comment

register = Library()


@register.assignment_tag
def get_latest_comments(**kwargs):
    """
    Select and return *count* latest discussion comments.

    Usage:

        {% get_latest_comments count=<int> as result %}

    Example:

        {% get_latest_comments count=10 as latest_comments %}
    """
    count = kwargs['count']

    query = Comment.objects.select_related(
        'user', 'anonymous'
    ).order_by(
        '-timestamp'
    )

    return query[:count]
