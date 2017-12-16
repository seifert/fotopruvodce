
from django.template import Library

register = Library()


@register.simple_tag
def render_field_with_css(field, *extra_classes):
    """
    Render form *field* with extra css classes *extra_classes*.

    Usage:

        {% render_field_with_css field 'class1' 'class2' %}

    Example:

        {% render_field_with_css form.username 'form-control' %}
    """
    classes = field.field.widget.attrs.get('class')
    if extra_classes:
        if classes:
            new_classes = '{} {}'.format(classes, ' '.join(extra_classes))
        else:
            new_classes = ' '.join(extra_classes)
        field.field.widget.attrs['class'] = new_classes
        try:
            rendered_field = str(field)
        finally:
            field.field.widget.attrs['class'] = classes
    return rendered_field
