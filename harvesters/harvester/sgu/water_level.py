from dateutil import parser
from django.utils.timezone import make_aware

from gwml2.harvesters.harvester.sgu.abstract import SguAPI, SkipProcessWell
from gwml2.harvesters.models.harvester import (
    HarvesterWellData, Harvester
)
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_AMSL,
    WellLevelMeasurement
)


class SguWaterLevelAPI(SguAPI):
    """Harvester for
    https://www.sgu.se/grundvatten/grundvattennivaer/matstationer/."""
    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL)
        super(SguWaterLevelAPI, self).__init__(
            harvester, replace, original_id
        )

    def process_well(
            self, harvester_well_data: HarvesterWellData, note: str
    ):
        """Processing well.
        """
        well = harvester_well_data.well
        response = self._request_api(
            f'https://resource.sgu.se/oppnadata/grundvatten/api/'
            f'grundvattennivaer/nivaer/station/{well.original_id}?format=json'
        )
        try:
            feature = response['features'][0]
        except IndexError:
            raise SkipProcessWell()

        properties = feature['properties']
        original_id = properties['omrade-_och_stationsnummer']

        # Skip if it does not return the same station id
        if well.original_id != original_id:
            raise SkipProcessWell()

        self._update(note)

        # Check latest date
        last = well.welllevelmeasurement_set.order_by('-time').first()

        # Measurement total
        measurement_total = len(properties['Mätningar'])
        updated = False
        # ------------------------------------------
        # Measurements
        # ------------------------------------------
        for measurement_idx, measurement in enumerate(properties['Mätningar']):
            try:
                date_time = make_aware(
                    parser.parse(measurement['datum_for_matning'])
                )
                if not last or date_time > last.time:
                    self._update(
                        f'{note}'
                        f'measurement({measurement_idx}/{measurement_total})'
                    )
                    defaults = {
                        'parameter': self.parameter,
                        'value_in_m': measurement['grundvattenniva_m_o.h.']
                    }
                    self._save_measurement(
                        model=WellLevelMeasurement,
                        time=date_time,
                        defaults=defaults,
                        harvester_well_data=harvester_well_data,
                        value=measurement['grundvattenniva_m_o.h.'],
                        unit=self.unit_m
                    )
                    updated = True
            except KeyError:
                pass
        if updated:
            self.well_updated(well=well)
