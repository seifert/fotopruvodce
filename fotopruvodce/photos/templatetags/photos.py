
from django.template import Library

from fotopruvodce.photos.models import Photo, Comment

register = Library()


@register.assignment_tag
def get_latest_photos(**kwargs):
    """
    Select and return *count* latest photos.

    Usage:

        {% get_latest_photos count=<int> as result %}

    Example:

        {% get_latest_photos count=3 as latest_photos %}
    """
    count = kwargs['count']

    query = Photo.objects.select_related(
        'user', 'section'
    ).filter(
        deleted=False,
        active=True,
    ).order_by(
        '-timestamp'
    )

    return query[:count]


@register.assignment_tag
def get_latest_photos_comments(**kwargs):
    """
    Select and return *count* latest photos.

    Usage:

        {% get_latest_photos_comments count=<int> as result %}

    Example:

        {% get_latest_photos_comments count=3 as latest_photos_comments %}
    """
    count = kwargs['count']

    query = Comment.objects.select_related(
        'photo', 'photo__user', 'user'
    ).filter(
        photo__deleted=False, photo__active=True
    ).order_by(
        '-timestamp'
    )

    return query[:count]
