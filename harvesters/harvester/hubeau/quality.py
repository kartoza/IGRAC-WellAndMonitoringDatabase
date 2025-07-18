"""Harvester of using hubeau."""

from gwml2.harvesters.harvester.hubeau.base import HubeauHarvester


class HubeauWaterQuality(HubeauHarvester):
    """Harvester for Water Quality

    https://hubeau.eaufrance.fr/page/api-qualite-nappes
    """

    @property
    def station_url(self):
        """Return station url."""
        return "https://hubeau.eaufrance.fr/api/v1/qualite_nappes/stations"

    def _measurement_params_update(
            self, params_dict: dict, parameter_key: str
    ):
        """Return measurement url."""
        params_dict.update(
            {"code_param": parameter_key}
        )
        return params_dict

    @property
    def measurement_url(self):
        """Return measurement url."""
        return "https://hubeau.eaufrance.fr/api/v1/qualite_nappes/analyses"

    @property
    def measurement_fields(self) -> list[str]:
        """Measurement of fields to be returned."""
        return ["date_mesure", "niveau_nappe_eau"]

    @property
    def measurement_date_debut_key(self):
        """Measurement of date debut key."""
        return "date_debut_prelevement"

    @property
    def measurement_date_fin_key(self):
        """Measurement of date debut key."""
        return "date_fin_prelevement"

    @property
    def measurement_station_id_key(self):
        """Measurement of station id key."""
        return "bss_id"

    @property
    def measurement_date_key(self):
        """Measurement of date key."""
        return "date_debut_prelevement"

    @property
    def measurement_value_key(self):
        """Measurement of unit key."""
        return "resultat"
