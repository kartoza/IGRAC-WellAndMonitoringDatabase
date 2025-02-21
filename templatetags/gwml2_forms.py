from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_label(field, label=None):
    if not label:
        label = field.label

    if field.field.required:
        return f'<b>{label}</b>'
    else:
        return label


@register.simple_tag
def render_help_text(field, help_text=''):
    if field.help_text:
        help_text = field.help_text
    if help_text:
        help_text = '<i class="fa fa-question-circle-o" aria-hidden="true" data-toggle="tooltip" title="{}"></i>'.format(
            help_text)
    return mark_safe(help_text)


@register.simple_tag
def field_as_row(field, id='', unit='', help_text='', label=None):
    if id:
        id = 'id="{}"'.format(id)
    return mark_safe(
        '<tr {id} class="input-column">'
        '   <td>{label} {help_text}</td>'
        '   <td>'
        '       <div class="input">{input} {unit}</div>'
        '   </td>'
        '</tr>'.format(
            id=id,
            help_text=render_help_text(field, help_text),
            label=render_label(field, label),
            input=field,
            unit=unit
        ))


@register.simple_tag
def relation_list_url(well, theform):
    id = well.id if well.id else 0
    return reverse('well-relation-list', kwargs={
        'id': id,
        'model': theform.instance.__class__.__name__

    })


@register.simple_tag
def delete_url(well, instance):
    id = well.id if well.id else 0
    return reverse('well-relation-delete', kwargs={
        'id': id,
        'model': instance.__class__.__name__,
        'model_id': instance.id

    })


@register.simple_tag
def get_model_name(theform):
    return theform.instance.__class__.__name__
