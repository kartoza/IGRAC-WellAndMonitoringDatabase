# Generated by Django 4.2.17 on 2025-07-07 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gwml2", "0107_alter_harvesterparametermap_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="harvester",
            name="task_id",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sitepreference",
            name="running_harvesters",
            field=models.ManyToManyField(blank=True, to="gwml2.harvester"),
        ),
        migrations.AddField(
            model_name="sitepreference",
            name="running_harvesters_concurrency_count",
            field=models.IntegerField(default=2),
        ),
    ]
