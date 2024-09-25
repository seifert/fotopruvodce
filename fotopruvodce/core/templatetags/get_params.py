from urllib import parse

from django.template import Library

register = Library()


@register.simple_tag
def add_get_params(url, **kwargs):
    """
    Add get parameters into *url*.

    Usage:

        {% add_get_params url param1=value1 param2='value2' %}

    Example:

        {% add_get_params request.get_full_path p=objects.next_page_number %}
    """
    url_parts = parse.urlparse(url)
    qs_parts = parse.parse_qsl(url_parts.query)
    qs_parts.extend(kwargs.items())
    query = parse.urlencode(qs_parts)
    return parse.urlunparse(
        (
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_parts.params,
            query,
            url_parts.fragment,
        )
    )


@register.simple_tag
def replace_get_params(url, **kwargs):
    """
    Replace get parameters in *url*. If parameter doesn't exist, add it.

    Usage:

        {% replace_get_params url param1=value1 param2='value2' %}

    Example:

        {% replace_get_params request.get_full_path p=objects.next_page_number %}
    """
    url_parts = parse.urlparse(url)
    qs_parts = parse.parse_qsl(url_parts.query)

    # Replace first occurrence of the existing get parameter
    for i, part in enumerate(qs_parts):
        k = part[0]
        if k in kwargs:
            v = kwargs.pop(k)
            qs_parts[i] = (k, v)
    # Append not existing get parameters
    qs_parts.extend((k, v) for k, v in kwargs.items())

    query = parse.urlencode(qs_parts)
    return parse.urlunparse(
        (
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_parts.params,
            query,
            url_parts.fragment,
        )
    )


@register.simple_tag
def remove_get_params(url, *args):
    """
    Remove get parameters from *url*.

    Usage:

        {% remove_get_params url paramname1 'paramname2' %}

    Example:

        {% remove_get_params request.get_full_path 'page' %}
    """
    url_parts = parse.urlparse(url)
    qs_parts = [i for i in parse.parse_qsl(url_parts.query) if i[0] not in args]
    query = parse.urlencode(qs_parts)
    return parse.urlunparse(
        (
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_parts.params,
            query,
            url_parts.fragment,
        )
    )
