from django.contrib.gis.db import models


class _Term(models.Model):
    """ Abstract model for Term """
    name = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class TermDrillingMethod(_Term):
    """ List of drilling method."""

    pass


class TermFeatureType(_Term):
    """ List of feature type."""

    pass


class TermMeasurementParameter(_Term):
    """ List of parameter for measurement."""

    pass


class TermGroundwaterUse(_Term):
    """ List of groundwater use."""

    pass


class TermAquiferType(_Term):
    """ List of aquifer type."""

    pass


class TermConfinement(_Term):
    """ List of confinement."""

    pass
