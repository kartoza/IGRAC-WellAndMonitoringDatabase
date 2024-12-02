from geonode.base.models import License, RestrictionCodeType
from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermWellPurpose
)
from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.base_cache import get_data


class WellData:
    """Return well data based on excel file."""

    # cache
    feature_types = {}
    purposes = {}
    status = {}
    units = {}
    organisations = {}
    groundwater_uses = {}
    aquifer_types = {}
    confinements = {}

    def __init__(
            self, well: Well, feature_types: dict, purposes: dict,
            status: dict, units: dict,
            organisations: dict, groundwater_uses: dict,
            aquifer_types: dict, confinements: dict
    ):
        self.well = well
        self.feature_types = feature_types
        self.purposes = purposes
        self.status = status
        self.units = units
        self.organisations = organisations
        self.groundwater_uses = groundwater_uses
        self.aquifer_types = aquifer_types
        self.confinements = confinements

    @property
    def country(self) -> Country:
        """Return folder.."""
        return self.well.country

    def general_information(self) -> []:
        """General Information of well."""
        well = self.well
        return {
            'original_id': well.original_id,
            'name': well.name,
            'feature_type': well.feature_type_id,
            'purpose': get_data(well.purpose_id, self.purposes,
                                TermWellPurpose),
            'status': well.status_id,
            'description': well.description,
            'latitude': well.location.y,
            'longitude': well.location.x,

            'ground_surface_elevation_value': well.ground_surface_elevation.value if well.ground_surface_elevation else '',
            'ground_surface_elevation_unit': get_data(
                well.ground_surface_elevation.unit_id, self.units, Unit)
            if well.ground_surface_elevation else '',

            'glo_90m_elevation_value': well.glo_90m_elevation.value if well.glo_90m_elevation else '',
            'glo_90m_elevation_unit': get_data(
                well.glo_90m_elevation.unit_id, self.units, Unit)
            if well.glo_90m_elevation else '',

            'top_borehole_elevation_value': well.top_borehole_elevation.value if well.top_borehole_elevation else '',
            'top_borehole_elevation_unit': get_data(
                well.top_borehole_elevation.unit_id, self.units, Unit)
            if well.top_borehole_elevation else '',
            'country': self.country.pk,
            'address': well.address
        }

    def license(self) -> []:
        """Return init license data."""
        well = self.well
        license = ''
        if well.license:
            try:
                license = License.objects.get(id=well.license).name
            except License.DoesNotExist:
                pass
        restriction_code_type = ''
        if well.restriction_code_type:
            try:
                restriction_code_type = RestrictionCodeType.objects.get(
                    id=well.restriction_code_type).description
            except RestrictionCodeType.DoesNotExist:
                pass
        return {
            'organisation': self.well.organisation.name,
            'license': license,
            'restriction_code_type': restriction_code_type,
            'constraints_other': self.well.constraints_other
        }

    def management(self) -> []:
        """Return init management data."""
        well = self.well
        management = well.management
        return {
            "manager": management.manager if management else '',
            "description": management.description if management else '',
            "groundwater_use": management.groundwater_use_id,
            "number_of_users": management.number_of_users if management else ''
        }

    def management_license(self) -> []:
        """Return init management data."""
        well = self.well
        management = well.management
        license = management.license if management else None
        return {
            "number": license.number if license else '',
            "valid_from": license.valid_from.strftime('%Y-%m-%d')
            if license and license.valid_from else '',
            "valid_until": license.valid_until.strftime('%Y-%m-%d')
            if management and license and license.valid_until else '',
            "description": license.description if license else ''
        }

    def hydrogeology(self) -> []:
        """Return init pumping test data."""
        well = self.well
        hydrogeology = well.hydrogeology_parameter
        return {
            "aquifer_name": (
                hydrogeology.aquifer_name if hydrogeology else ''
            ),
            "aquifer_material": (
                hydrogeology.aquifer_material if hydrogeology else ''
            ),
            "aquifer_type": hydrogeology.aquifer_type_id
            if hydrogeology else '',
            "aquifer_thickness": hydrogeology.aquifer_thickness
            if hydrogeology and hydrogeology.aquifer_thickness else '',
            "confinement": hydrogeology.confinement_id,
            "degree_of_confinement": (
                hydrogeology.degree_of_confinement if hydrogeology else ''
            )
        }

    def pumping_test(self) -> []:
        """Return init pumping test data."""
        well = self.well
        hydrogeology = well.hydrogeology_parameter
        pumping_test = hydrogeology.pumping_test if hydrogeology else None
        hydraulic_conductivity = pumping_test.hydraulic_conductivity if pumping_test else None
        transmissivity = pumping_test.transmissivity if pumping_test else None
        specific_storage = pumping_test.specific_storage if pumping_test else None
        specific_capacity = pumping_test.specific_capacity if pumping_test else None
        storativity = pumping_test.storativity if pumping_test else None
        return {
            "porosity": pumping_test.porosity if pumping_test else '',
            "hydraulic_conductivity_value": (
                hydraulic_conductivity.value if hydraulic_conductivity else ''
            ),
            "hydraulic_conductivity_unit": get_data(
                hydraulic_conductivity.unit_id, self.units, Unit)
            if hydraulic_conductivity else '',
            "transmissivity_value": (
                transmissivity.value if transmissivity else ''
            ),
            "transmissivity_unit": get_data(
                transmissivity.unit_id, self.units, Unit
            )
            if transmissivity else '',
            "specific_storage_value": (
                specific_storage.value if specific_storage else ''
            ),
            "specific_storage_unit": get_data(
                specific_storage.unit_id, self.units, Unit
            )
            if specific_storage else '',
            "specific_capacity_value": (
                specific_capacity.value if specific_capacity else ''
            ),
            "specific_capacity_unit": get_data(
                specific_capacity.unit_id, self.units, Unit
            )
            if specific_capacity else '',
            "storativity_value": storativity.value if storativity else '',
            "storativity_unit": get_data(storativity.unit_id, self.units, Unit)
            if storativity else '',
            "test_type": pumping_test.test_type if pumping_test else ''
        }
