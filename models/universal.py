from django.contrib.gis.db import models


class Quantity(models.Model):
    """ Model to define quantity. """
    value = models.FloatField(
        null=True, blank=True)
    unit = models.TextField(
        null=True, blank=True)

    def __str__(self):
        return '{} ({})'.format(self.value, self.unit)


class GWTerm(models.Model):
    """ Abstract model for Term """
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class PositionalAccuracyType(GWTerm):
    """Description of the accuracy of the elevation measurement."""

    pass


class ElevationMeasurementMethodType(GWTerm):
    """Method used to measure the elevation, e.g. GPS, Survey, DEM, etc."""

    pass


class ElevationTypeTerm(GWTerm):
    """Type of reference elevation, defined as a feature, e.g. Top of Casing, Ground, etc."""

    pass


class Elevation(models.Model):
    """
    7.6.2 Elevation
    Elevation of a feature in reference to a datum.

    """

    # TODO we need to ask details about the elevation whether it's actually just a point or 3D point.
    elevation = models.PointField(
        null=False, blank=False, verbose_name="elevation",
        help_text="Numeric value, coordinate reference system (CRS), "
                  "and unit of measure (UoM) for the elevation.")
    elevation_accuracy = models.ForeignKey(
        PositionalAccuracyType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="elevationAccuracy",
        help_text="Description of the accuracy of the elevation measurement.")
    elevation_measurement_method = models.ForeignKey(
        ElevationMeasurementMethodType, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="elevationMeasurementMethod",
        help_text="Description of the accuracy of the elevation measurement.")
    elevation_type = models.ForeignKey(
        ElevationTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="elevationType",
        help_text="Type of reference elevation, defined as a feature, e.g. Top of Casing, Ground, etc.")


class NamedValue(models.Model):
    """
    NamedValue stores arbitrary event-specific parameter.
    """

    name = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class DocumentCitation(models.Model):
    """
    7.6.1 DocumentCitation
    The class DocumentCitation is abstract, and has no attributes, operations or associations.
    It serves as a placeholder for legislative and reference documentation for a management
    area. Legislative documentation refers to the legal instrument or document that required
    the establishment of the management area. Reference documentation might describe the
    environmental objectives and measures that are to be undertaken in the management area
    to protect the environment (a reference to a management or action plan), licensing
    information, and associated maps.
    The 'Legislation References' and 'DocumentCitation' classes from the INSPIRE Generic
    Conceptual Model are possible candidates for DocumentCitation.
    """

    name = models.TextField()
    date = models.DateField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class TemporalType(GWTerm):
    """
    Refers to the duration, instant or interval of the
    flow (actual time, not observation time). E.g.
    "yearly", "summer", "2009" or "2009-2011".
    """
    pass
