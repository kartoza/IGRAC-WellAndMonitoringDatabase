from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_label(field):
    label = field.label
    if field.field.required:
        return f'<b>{label}</b>'
    else:
        return label


@register.simple_tag
def field_as_row(field, id='', unit='', help_text=''):
    if field.help_text:
        help_text = field.help_text
    if help_text:
        help_text = '<i class="fa fa-question-circle-o" aria-hidden="true" data-toggle="tooltip" title="{}">'.format(
            help_text)
    if id:
        id = 'id="{}"'.format(id)
    return mark_safe(
        '<tr {id}>'
        '   <td>{label} {help_text}</i></td>'
        '   <td>'
        '       <div class="input">{input} {unit}</div>'
        '   </td>'
        '</tr>'.format(
            id=id,
            help_text=help_text,
            label=render_label(field),
            input=field,
            unit=unit
        ))
