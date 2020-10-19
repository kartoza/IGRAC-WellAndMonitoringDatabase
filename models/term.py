from django.contrib.gis.db import models
from adminsortable.models import Sortable


class _Term(Sortable):
    """ Abstract model for Term """

    name = models.CharField(
        max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class TermWellStatus(_Term):
    """ List of well status term."""

    class Meta(Sortable.Meta):
        db_table = 'term_well_status'


class TermWellPurpose(_Term):
    """ List of well purpose term."""

    class Meta(Sortable.Meta):
        db_table = 'term_well_purpose'


class TermDrillingMethod(_Term):
    """ List of drilling method."""

    class Meta(Sortable.Meta):
        db_table = 'term_drilling_method'


class TermFeatureType(_Term):
    """ List of feature type."""

    class Meta(Sortable.Meta):
        db_table = 'term_feature_type'


class TermMeasurementParameter(_Term):
    """ List of parameter for measurement."""

    class Meta(Sortable.Meta):
        db_table = 'term_measurement_parameter'


class TermMeasurementParameterGroup(_Term):
    """ List of parameter for measurement."""
    parameters = models.ManyToManyField(
        TermMeasurementParameter,
        null=True, blank=True
    )

    class Meta(Sortable.Meta):
        db_table = 'term_measurement_parameter_group'


class TermGroundwaterUse(_Term):
    """ List of groundwater use."""

    class Meta(Sortable.Meta):
        db_table = 'term_groundwater_use'


class TermAquiferType(_Term):
    """ List of aquifer type."""

    class Meta(Sortable.Meta):
        db_table = 'term_aquifer_type'


class TermConfinement(_Term):
    """ List of confinement."""

    class Meta(Sortable.Meta):
        db_table = 'term_confinement'


class TermReferenceElevationType(_Term):
    """ The type of reference for elevation
    """

    class Meta(Sortable.Meta):
        db_table = 'term_reference_elevation_type'


class TermConstructionStructureType(_Term):
    """ The type of construction structure
    """

    class Meta(Sortable.Meta):
        db_table = 'term_construction_structure_type'
