# Generated by Django 2.2.16 on 2022-06-29 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0056_view_well'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='downloadsessionuser',
            name='session',
        ),
        migrations.DeleteModel(
            name='DownloadSession',
        ),
        migrations.DeleteModel(
            name='DownloadSessionUser',
        ),
    ]