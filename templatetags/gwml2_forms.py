import copy
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_label(field):
    label = field.label
    if field.field.required:
        return f'<b>{label}*</b>'
    else:
        return label


@register.simple_tag
def field_as_row(field, unit=''):
    return mark_safe(
        '<tr><td>{label}</td><td>{input} {unit}</td></tr>'.format(
            label=render_label(field),
            input=field,
            unit=unit
        ))
