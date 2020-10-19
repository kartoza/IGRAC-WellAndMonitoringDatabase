# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
from django.db import migrations


def import_data(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    app_name = 'gwml2'
    DJANGO_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))

    # unit fixture
    fixture_file = os.path.join(
        DJANGO_ROOT, 'gwml2', 'fixtures', 'unit.json')
    with open(fixture_file) as json_file:
        data = json.load(json_file)
        Unit = apps.get_model(app_name, "Unit")
        UnitGroup = apps.get_model(app_name, "UnitGroup")
        for unit_name, value in data.items():
            unit, created = Unit.objects.using(db_alias).get_or_create(
                name=unit_name.lower(),
                defaults={
                    'description': value['description'] if 'description' in value else None,
                    'html': value['html'] if 'html' in value else None,
                }
            )
            for group_name in value['groups']:
                group, created = UnitGroup.objects.using(db_alias).get_or_create(
                    name=group_name.lower()
                )
                group.units.add(unit)

    # term fixture
    fixture_file = os.path.join(
        DJANGO_ROOT, 'gwml2', 'fixtures', 'term.json')
    with open(fixture_file) as json_file:
        data = json.load(json_file)
        for model_name, terms in data.items():
            Model = apps.get_model(app_name, model_name)
            for term in terms:
                Model.objects.using(db_alias).get_or_create(
                    name=term
                )

    # country fixture
    fixture_file = os.path.join(
        DJANGO_ROOT, 'gwml2', 'fixtures', 'country.json')
    with open(fixture_file) as json_file:
        data = json.load(json_file)
        Country = apps.get_model(app_name, "Country")
        for country in data:
            Country.objects.using(db_alias).get_or_create(
                name=country['name'],
                defaults={
                    'code': country['code']
                }
            )

    # measurement fixture
    fixture_file = os.path.join(
        DJANGO_ROOT, 'gwml2', 'fixtures', 'measurement_parameter.json')
    with open(fixture_file) as json_file:
        data = json.load(json_file)
        Measurement = apps.get_model(app_name, "TermMeasurementParameter")
        MeasurementGroup = apps.get_model(app_name, "TermMeasurementParameterGroup")
        for measurement_name, value in data.items():
            measurement, created = Measurement.objects.using(db_alias).get_or_create(
                name=measurement_name,
                defaults={
                    'description': value['description'] if 'description' in value else None
                }
            )
            for group_name in value['groups']:
                group, created = MeasurementGroup.objects.using(db_alias).get_or_create(
                    name=group_name
                )
                group.parameters.add(measurement)


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('gwml2', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_data),
    ]
