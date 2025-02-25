from gwml2.management.commands.base import WellCommand
from gwml2.models.well import WellLevelMeasurement, Well


class Command(WellCommand):
    """Convert measurement from a parameter to new parameter."""
    args = ''
    help = 'Convert measurement from a parameter to new parameter.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-from_measurement_id',
            '--from_measurement_id',
            dest='from_measurement_id',
            default='',
            help='Id of source measurement to convert'
        )
        parser.add_argument(
            '-to_measurement_id',
            '--to_measurement_id',
            dest='to_measurement_id',
            default='',
            help='Id of target measurement'
        )

    def handle(self, *args, **options):
        # Filter by from_id
        from_measurement_id = options.get('from_measurement_id', None)
        to_measurement_id = options.get('to_measurement_id', None)

        if not from_measurement_id:
            return
        if not to_measurement_id:
            return
        if from_measurement_id == to_measurement_id:
            return

        well_ids = self.well_ids(**options)
        count = len(well_ids)
        for idx, id in enumerate(well_ids):
            well = Well.objects.get(id=id)
            measurements = WellLevelMeasurement.objects.filter(
                well_id=well
            ).filter(
                parameter_id=from_measurement_id
            )
            measurement_count = measurements.count()
            print(
                f'----- {idx + 1}/{count} - {id} - '
                f'measurements {measurement_count} -----'
            )
            if measurement_count:
                measurements.update(
                    parameter_id=to_measurement_id
                )
                well.generate_all_measurement_caches(
                    measurement_name=None,
                    force=True
                )
