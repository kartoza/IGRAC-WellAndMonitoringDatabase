from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from gwml2.models.well import Well
from gwml2.utilities import temp_disconnect_signal


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Update measurement type of well.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-from',
            '--from',
            default='0',
            dest='from',
            help='From'
        )

    def handle(self, *args, **options):
        from gwml2.signals.well import update_well
        _from = int(options['from'])
        with temp_disconnect_signal(
                signal=post_save,
                receiver=update_well,
                sender=Well
        ):
            for idx, well in enumerate(Well.objects.all()):
                if idx + 1 < _from:
                    continue
                well.assign_measurement_type()
                well.save()
