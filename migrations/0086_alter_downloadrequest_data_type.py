# Generated by Django 3.2.20 on 2024-06-18 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0085_view_well'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadrequest',
            name='data_type',
            field=models.CharField(choices=[('GGMN', 'GGMN'), ('Well and Monitoring Data', 'Other data')], default='GGMN', max_length=512, verbose_name='Data type'),
        ),
    ]