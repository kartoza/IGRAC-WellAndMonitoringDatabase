# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import os
from django.db import migrations
from django.core.management import call_command


def import_data(apps, schema_editor):
    # TODO :
    #  call command update_fixtures
    pass


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('gwml2', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_data),
    ]
