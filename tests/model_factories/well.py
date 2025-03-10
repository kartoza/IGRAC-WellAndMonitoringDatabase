"""Factory for Well."""
import factory
from django.contrib.gis.geos import Point
from django.utils.timezone import now

from gwml2.models.general import Quantity
from gwml2.models.well import (
    Well, WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)
from gwml2.tests.model_factories import OrganisationF


class WellF(factory.django.DjangoModelFactory):
    """Factory for Well."""

    name = factory.Sequence(lambda n: 'well_{}'.format(n))
    original_id = factory.Sequence(lambda n: 'well_{}'.format(n))
    organisation = factory.SubFactory(OrganisationF)
    location = Point(0, 0)

    class Meta:  # noqa: D106
        model = Well


def create_quantity():
    """Function to create and return a Quantity instance."""
    return Quantity.objects.create(value=1)


class _MeasurementF(factory.django.DjangoModelFactory):
    """Factory for Well."""

    time = factory.LazyFunction(now)
    methodology = factory.Faker('sentence', nb_words=6)
    value = factory.LazyFunction(create_quantity)

    class Meta:  # noqa: D106
        model = Well


class WellLevelMeasurementF(_MeasurementF):
    """Well level measurement factory."""

    class Meta:  # noqa: D106
        model = WellLevelMeasurement


class WellQualityMeasurementF(_MeasurementF):
    """Well quality measurement factory."""

    class Meta:  # noqa: D106
        model = WellQualityMeasurement


class WellYieldMeasurementF(_MeasurementF):
    """Well yield measurement factory."""

    class Meta:  # noqa: D106
        model = WellYieldMeasurement
