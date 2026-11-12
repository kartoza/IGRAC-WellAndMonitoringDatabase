"""England - Environment Agency Hydrology API

API: https://environment.data.gov.uk/hydrology/doc/reference
"""

import requests

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models import Harvester
from gwml2.models import (
    MEASUREMENT_PARAMETER_AMSL,
    TermMeasurementParameter,
    Unit,
)
from gwml2.models.general import Quantity
from gwml2.models.geology import Geology
from gwml2.models.term import TermReferenceElevationType, TermWellStatus
from gwml2.models.well import HydrogeologyParameter


class EnglandLevelHarvester(BaseHarvester):
    """England - Environment Agency Hydrology API

    API: https://environment.data.gov.uk/hydrology/doc/reference
    """

    offset_attribute_key = "offset"
    LIMIT = 10000

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        """Save the harvester for scotland SEPA."""
        self.level_parameter = TermMeasurementParameter.objects.get(name=MEASUREMENT_PARAMETER_AMSL)
        try:
            self.unit = Unit.objects.get(name="m")
        except Unit.DoesNotExist:
            raise Exception("Unit m does not exist")

        self.statuses = {}
        super(EnglandLevelHarvester, self).__init__(harvester, replace, original_id)

    def get_stations(self):
        """Return stations."""
        response = requests.get(
            "https://environment.data.gov.uk/hydrology/id/stations.json",
            params={
                "_limit": self.LIMIT,
                "observedProperty": "groundwaterLevel",
                "_offset": self.current_offset,
            },
        )
        return response.json()["items"]

    def get_status(self, station) -> TermWellStatus | None:
        """Return TermWellStatus from station status label.

        Just return if it is found on TermWellStatus.
        """
        statuses = station.get("status") or []
        if isinstance(statuses, dict):
            statuses = [statuses]
        for status in statuses:
            label = status.get("label") if isinstance(status, dict) else None
            if not label:
                continue
            key = label.lower()
            if key not in self.statuses:
                self.statuses[key] = TermWellStatus.objects.filter(name__iexact=label).first()
            if self.statuses[key]:
                return self.statuses[key]
        return None

    def _process(self):
        """Run the harvester."""
        # Get latest offset
        self.current_offset = int(self.attributes.get(self.offset_attribute_key, "0"))

        while True:
            self._update(f"Fetching stations : offset {self.current_offset}")
            stations = self.get_stations()

            # If empty, break the loop
            if not stations:
                break

            # Loop the station
            total = len(stations)
            for idx, station in enumerate(stations):
                self.log_prefix = f"{idx + 1}/{total} offset - {self.current_offset}"
                original_id = station["wiskiID"]

                # Check the well
                # If it resumed and not the current one, skip it
                self.check_current_well(original_id)
                if not self.is_processing_station:
                    continue

                try:
                    name = station["label"]
                    latitude = station["lat"]
                    longitude = station["long"]
                    borehole_depth = station.get("boreholeDepth", None)
                    aquifer = station.get("aquifer", None)

                    # Save to well
                    well = self._save_well(
                        original_id=original_id,
                        name=name,
                        latitude=latitude,
                        longitude=longitude,
                    )
                    # Total depth
                    if borehole_depth is not None:
                        if not well.geology:
                            well.geology = Geology.objects.create(
                                reference_elevation=TermReferenceElevationType.objects.filter(
                                    name="Ground Surface Level ASL"
                                ).first()
                            )
                        geology = well.geology
                        if geology.total_depth:
                            geology.total_depth.value = float(borehole_depth)
                            geology.total_depth.unit = self.unit
                            geology.total_depth.save()
                        else:
                            geology.total_depth = Quantity.objects.create(
                                value=float(borehole_depth), unit=self.unit
                            )
                            geology.save()
                    # Aquifer
                    if aquifer:
                        if not well.hydrogeology_parameter:
                            well.hydrogeology_parameter = HydrogeologyParameter.objects.create()
                        well.hydrogeology_parameter.aquifer_name = aquifer
                        well.hydrogeology_parameter.save()

                    # Save well status
                    status = self.get_status(station)
                    if status:
                        well.status = status
                    well.save()
                except Exception as e:
                    self.log.log_well(original_id, "Error", str(e))

            self.current_offset += self.LIMIT
            self.update_attribute(self.offset_attribute_key, self.current_offset)

        # Reset so the following caches/done logs in base are not prefixed
        self.log_prefix = ""
        self.delete_attribute(self.offset_attribute_key)
