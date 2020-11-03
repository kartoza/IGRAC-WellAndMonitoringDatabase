import math
from django.db.models import Q
from gwml2.models.well_management.organisation import Organisation


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_organisations_as_viewer(user):
    """ return organisation of user as viewer"""
    if user.is_staff:
        return Organisation.objects.all().order_by('id')
    else:
        return Organisation.objects.filter(
            Q(editors__contains=[user.id]) | Q(admins__contains=[user.id]) | Q(viewers__contains=[user.id])
        ).order_by('id')


def get_organisations(user):
    """ return organisation of user """
    if user.is_staff:
        return Organisation.objects.all()
    else:
        return Organisation.objects.filter(
            Q(editors__contains=[user.id]) | Q(admins__contains=[user.id]))


def allow_to_edit_well(user):
    """ is the user allowed to edit """
    return get_organisations(user).count()
