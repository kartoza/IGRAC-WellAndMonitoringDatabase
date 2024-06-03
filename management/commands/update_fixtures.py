import json
import os
from django.apps import apps
from django.core.management.base import BaseCommand
from gwml2.models import (
    Country, Unit, UnitConvertion, UnitGroup,
    TermMeasurementParameter, TermMeasurementParameterGroup
)


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Reupdate all fixtures.'

    def handle(self, *args, **options):
        app_name = 'gwml2'
        DJANGO_ROOT = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
        fixture_folder = os.path.join(
            DJANGO_ROOT, 'fixtures')

        # unit fixture
        fixture_file = os.path.join(fixture_folder, 'unit.json')
        with open(fixture_file) as json_file:
            data = json.load(json_file)
            for unit_name, value in data.items():
                unit, created = Unit.objects.get_or_create(
                    name=unit_name,
                    defaults={
                        'description': value['description'] if 'description' in value else None,
                        'html': value['html'] if 'html' in value else None,
                    }
                )
                for group_name in value['groups']:
                    group, created = UnitGroup.objects.get_or_create(
                        name=group_name
                    )
                    group.units.add(unit)

        # unit_conversion fixture
        fixture_file = os.path.join(fixture_folder, 'unit_conversion.json')
        with open(fixture_file) as json_file:
            data = json.load(json_file)
            for unit_from, value in data.items():
                unit_from = Unit.objects.get(name=unit_from)
                for unit_to, formula in value.items():
                    unit_to = Unit.objects.get(name=unit_to)
                    UnitConvertion.objects.get_or_create(
                        unit_from=unit_from,
                        unit_to=unit_to,
                        defaults={
                            'formula': formula
                        }
                    )

        # term fixture
        fixture_file = os.path.join(fixture_folder, 'term.json')
        with open(fixture_file) as json_file:
            data = json.load(json_file)
            for model_name, terms in data.items():
                Model = apps.get_model(app_name, model_name)
                for term in terms:
                    Model.objects.get_or_create(
                        name=term
                    )

        # country fixture
        fixture_file = os.path.join(fixture_folder, 'country.json')
        with open(fixture_file) as json_file:
            data = json.load(json_file)
            for country in data:
                Country.objects.get_or_create(
                    name=country['name'],
                    defaults={
                        'code': country['code']
                    }
                )

        # measurement fixture
        fixture_file = os.path.join(fixture_folder, 'measurement_parameter.json')
        with open(fixture_file) as json_file:
            data = json.load(json_file)
            for measurement_name, value in data.items():
                measurement, created = TermMeasurementParameter.objects.get_or_create(
                    name=measurement_name,
                    defaults={
                        'description': value['description'] if 'description' in value else None
                    }
                )
                for group_name in value['groups']:
                    group, created = TermMeasurementParameterGroup.objects.get_or_create(
                        name=group_name
                    )
                    group.parameters.add(measurement)
                units = Unit.objects.filter(name__in=value['units'])
                measurement.units.add(*units)
                try:
                    measurement.default_unit = Unit.objects.get(
                        name=value['default_unit']
                    )
                except (Unit.DoesNotExist, KeyError):
                    pass
                measurement.save()
