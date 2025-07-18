"""Harvester of using hubeau."""

from gwml2.harvesters.harvester.hubeau.base import HubeauHarvester
from gwml2.harvesters.models import Harvester, HarvesterParameterMap
from gwml2.models import (
    Unit, TermMeasurementParameter, MEASUREMENT_PARAMETER_AMSL
)


class HubeauWaterLevel(HubeauHarvester):
    """
    Harvester for https://hubeau.eaufrance.fr/page/api-piezometrie

    attributes :
    - codes : List of code_bss
              Limit the codes that will be fetched.
    """

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        # Create this as default
        HarvesterParameterMap.objects.get_or_create(
            key="level",
            harvester=harvester,
            parameter=self.parameter,
            defaults={
                "parameter": self.parameter,
                "unit": self.unit_m
            }
        )
        super(HubeauWaterLevel, self).__init__(
            harvester, replace, original_id
        )

    @property
    def station_url(self):
        """Return station url."""
        return (
            "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations?"
            "format=json&nb_mesures_piezo_min=2&size=2000"
        )

    def _measurement_params_update(
            self, params_dict: dict, parameter_key: str
    ):
        """Return measurement url."""
        return params_dict

    @property
    def measurement_url(self):
        """Return measurement url."""
        return "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques"

    @property
    def measurement_fields(self) -> list[str]:
        """Measurement of fields to be returned."""
        return ["date_mesure", "niveau_nappe_eau"]

    @property
    def measurement_date_debut_key(self):
        """Measurement of date debut key."""
        return "date_debut_mesure"

    @property
    def measurement_date_fin_key(self):
        """Measurement of date debut key."""
        return "date_fin_mesure"

    @property
    def measurement_station_id_key(self):
        """Measurement of station id key."""
        return "code_bss"

    @property
    def measurement_date_key(self):
        """Measurement of date key."""
        return "date_mesure"

    @property
    def measurement_value_key(self):
        """Measurement of unit key."""
        return "niveau_nappe_eau"
