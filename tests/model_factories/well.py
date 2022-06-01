"""Factory for Well."""
import factory
from django.contrib.gis.geos import Point

from gwml2.models.well import Well
from gwml2.tests.model_factories import OrganisationF


class WellF(factory.django.DjangoModelFactory):
    """Factory for Well."""

    name = factory.Sequence(lambda n: 'well_{}'.format(n))
    original_id = factory.Sequence(lambda n: 'well_{}'.format(n))
    organisation = factory.SubFactory(OrganisationF)
    location = Point(0, 0)

    class Meta:  # noqa: D106
        model = Well
