# Generated by Django 3.2.20 on 2024-03-22 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0079_alter_harvesterattribute_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadrequest',
            name='organisations',
            field=models.ManyToManyField(blank=True, null=True, related_name='download_organisation_data_request', to='gwml2.Organisation'),
        ),
    ]