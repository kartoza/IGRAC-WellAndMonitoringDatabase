# Generated by Django 2.2.16 on 2022-09-01 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0060_auto_20220901_0423'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadsession',
            name='constraints_other',
            field=models.TextField(blank=True, help_text='other restrictions and legal prerequisites for accessing and using the resource or metadata', null=True, verbose_name='restrictions other'),
        ),
        migrations.AddField(
            model_name='uploadsession',
            name='license',
            field=models.IntegerField(blank=True, help_text='license of the dataset. this is ID of license in geonode.', null=True, verbose_name='License'),
        ),
        migrations.AddField(
            model_name='uploadsession',
            name='restriction_code_type',
            field=models.IntegerField(blank=True, help_text='limitation(s) placed upon the access or use of the data. this is ID of restriction code in geonode.', null=True, verbose_name='Restrictions'),
        ),
    ]
