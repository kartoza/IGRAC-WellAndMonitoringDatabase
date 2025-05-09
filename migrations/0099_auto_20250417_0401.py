# Generated by Django 3.2.20 on 2025-04-17 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0098_sitepreference_batch_upload_auto_resume'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadsession',
            name='checkpoint',
            field=models.IntegerField(choices=[(1, 'Saving data'), (2, 'Cache wells'), (3, 'Cache country'), (4, 'Cache organisation'), (5, 'Create report'), (6, 'Finish')], default=1),
        ),
        migrations.AddField(
            model_name='uploadsession',
            name='checkpoint_ids',
            field=models.JSONField(blank=True, help_text='This is the ids for the checkpoint, e.g: list of wells id for CACHE_COUNTRY checkpoint', null=True),
        ),
    ]
