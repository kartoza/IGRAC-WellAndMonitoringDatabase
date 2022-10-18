"""Factory for Organisation."""
import factory

from gwml2.models.well_management.organisation import Organisation


class OrganisationF(factory.django.DjangoModelFactory):
    """Factory for Organisation."""

    name = factory.Sequence(lambda n: 'organisation_{}'.format(n))

    class Meta:  # noqa: D106
        model = Organisation
