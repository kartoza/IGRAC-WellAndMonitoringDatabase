import math
import os
import subprocess
import typing
from typing import List

from django.db.models import Q
from django.utils.timezone import make_aware

from gwml2.models.general import Unit, UnitConvertion, Quantity
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
            Q(editors__contains=[user.id]) | Q(admins__contains=[user.id])
        ).order_by('id')


def get_organisations_as_admin(user):
    """ return organisation of user as viewer"""
    if user.is_staff:
        return Organisation.objects.all().order_by('id')
    else:
        return Organisation.objects.filter(
            admins__contains=[user.id]).order_by('id')


def get_organisations_as_editor(user):
    """ return organisation of user """
    if user.is_staff:
        return Organisation.objects.all()
    else:
        return Organisation.objects.filter(
            Q(editors__contains=[user.id]) | Q(admins__contains=[user.id]))


def allow_to_edit_well(user):
    """ is the user allowed to edit """
    return get_organisations_as_editor(user).count()


class temp_disconnect_signal(object):
    """ Temporarily disconnect a model from a signal """

    def __init__(self, signal, receiver, sender):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender
        )

    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender
        )


class Signal(object):
    """Signal object."""

    def __init__(self, signal, receiver, sender):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender


class temp_disconnect_signals(object):
    """ Temporarily disconnect signals in list """

    def __init__(self, signals: List[Signal]):
        self.signals = signals

    def __enter__(self):
        for signal in self.signals:
            signal.signal.disconnect(
                receiver=signal.receiver,
                sender=signal.sender
            )

    def __exit__(self, type, value, traceback):
        for signal in self.signals:
            signal.signal.connect(
                receiver=signal.receiver,
                sender=signal.sender
            )


def convert_value(quantity: Quantity, unit_to: Unit) -> typing.Optional[
    Quantity]:
    """ Get value of quantity
    convert to unit_to
    """
    if quantity:
        value = quantity.value
        unit = quantity.unit
        if quantity.unit and quantity.unit != unit_to:
            try:
                value = eval(
                    UnitConvertion.objects.get(
                        unit_from=quantity.unit,
                        unit_to=unit_to
                    ).formula.replace('x', '{}'.format(value))
                )
                unit = unit_to
            except (UnitConvertion.DoesNotExist, KeyError) as e:
                pass
            except ValueError as e:
                print(e)
        return Quantity(
            unit=unit, value=value)
    else:
        return None


def make_aware_local(time):
    """Make aware."""
    try:
        return make_aware(time)
    except (ValueError, AttributeError):
        return time


def xlsx_to_ods(filename):
    """Convert xlsx to ods."""
    subprocess.call(
        [
            'soffice', '--headless', '--invisible', '--convert-to', 'ods',
            filename, '--outdir', os.path.dirname(filename)
        ]
    )


def ods_to_xlsx(filename):
    """Convert xlsx to ods."""
    subprocess.call(
        [
            'soffice', '--headless', '--invisible', '--convert-to', 'xlsx',
            filename, '--outdir', os.path.dirname(filename)
        ]
    )
    return filename.replace('.ods', '.xlsx')
