from django import template
from gwml2.utilities import allow_to_edit_well, get_organisations_as_admin

register = template.Library()


@register.simple_tag(name='allow_to_edit')
def allow_to_edit(user):
    """ is the user allowed to edit """
    return allow_to_edit_well(user)


@register.simple_tag(name='is_admin')
def is_admin(user):
    """ is the user allowed to edit """
    return get_organisations_as_admin(user).count() > 0
