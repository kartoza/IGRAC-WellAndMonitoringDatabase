# Generated by Django 3.2.20 on 2023-11-24 08:18

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0073_downloadrequest_is_ready'),
    ]

    operations = [
        migrations.CreateModel(
            name='WellDeletion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField(blank=True, null=True)),
                ('start_at', models.DateTimeField(default=datetime.datetime.now)),
                ('identifier', models.UUIDField(default=uuid.uuid4, editable=False, null=True)),
                ('ids', models.JSONField()),
                ('data', models.JSONField()),
                ('progress', models.IntegerField(default=0)),
            ],
        ),
    ]