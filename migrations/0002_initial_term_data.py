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

    fixture_file = os.path.join(
        DJANGO_ROOT, 'gwml2', 'fixtures', 'unit.json')
    with open(fixture_file) as json_file:
        data = json.load(json_file)
        Unit = apps.get_model(app_name, "Unit")
        UnitGroup = apps.get_model(app_name, "UnitGroup")
        for unit_name, value in data.items():
            unit, created = Unit.objects.using(db_alias).get_or_create(
                name=unit_name.lower(),
                defaults={'description': value['description']}
            )
            for group_name in value['groups']:
                group, created = UnitGroup.objects.using(db_alias).get_or_create(
                    name=group_name.lower()
                )
                group.units.add(unit)


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('gwml2', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_data),
    ]
