from django.contrib.gis.db import models


class _Term(models.Model):
    """ Abstract model for Term """

    name = models.CharField(
        max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    wagtail_reference_index_ignore = True

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['name']


class TermWellStatus(_Term):
    """ List of well status term."""

    class Meta:
        verbose_name_plural = 'Term well status'
        verbose_name = 'Term well status'
        db_table = 'term_well_status'
        ordering = ['name']


class TermWellPurpose(_Term):
    """ List of well purpose term."""

    class Meta:
        db_table = 'term_well_purpose'
        ordering = ['name']


class TermDrillingMethod(_Term):
    """ List of drilling method."""

    class Meta:
        db_table = 'term_drilling_method'
        ordering = ['name']


class TermFeatureType(_Term):
    """ List of feature type."""

    class Meta:
        db_table = 'term_feature_type'
        ordering = ['name']


class TermGroundwaterUse(_Term):
    """ List of groundwater use."""

    class Meta:
        db_table = 'term_groundwater_use'
        ordering = ['name']


class TermAquiferType(_Term):
    """ List of aquifer type."""

    class Meta:
        db_table = 'term_aquifer_type'
        ordering = ['name']


class TermConfinement(_Term):
    """ List of confinement."""

    class Meta:
        db_table = 'term_confinement'
        ordering = ['name']


class TermReferenceElevationType(_Term):
    """ The type of reference for elevation
    """

    class Meta:
        db_table = 'term_reference_elevation_type'
        ordering = ['name']


class TermConstructionStructureType(_Term):
    """ The type of construction structure
    """

    class Meta:
        db_table = 'term_construction_structure_type'
        ordering = ['name']
