from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

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
        '<tr {id} class="input-column">'
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


@register.simple_tag
def relation_list_url(well, theform):
    return reverse('well-relation-list', kwargs={
        'id': well.id,
        'model': theform.instance.__class__.__name__

    })


@register.simple_tag
def delete_url(well, instance):
    return reverse('well-relation-delete', kwargs={
        'id': well.id,
        'model': instance.__class__.__name__,
        'model_id': instance.id

    })


@register.simple_tag
def get_model_name(theform):
    return theform.instance.__class__.__name__
