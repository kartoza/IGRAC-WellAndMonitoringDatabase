from django import template
from gwml2.utilities import allow_to_edit_well

register = template.Library()


@register.simple_tag(name='allow_to_edit')
def allow_to_edit(user):
    """ is the user allowed to edit """
    return allow_to_edit_well(user)
