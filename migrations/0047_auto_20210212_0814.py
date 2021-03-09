# Generated by Django 2.2.16 on 2021-02-12 08:14

import datetime
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gwml2', '0046_unitconvertion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='construction',
            name='pump_description',
            field=models.TextField(blank=True, help_text='Any relevant information on the pump (e.g. model, capacity, energy supply, depth).', null=True, verbose_name='Pump description'),
        ),
        migrations.AlterField(
            model_name='construction',
            name='pump_installer',
            field=models.CharField(blank=True, help_text='Name of the company or person who installed the pump.', max_length=200, null=True, verbose_name='Pump installer'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='bottom_depth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='structure_bottom_depth', to='gwml2.Quantity', verbose_name='Bottom depth'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='diameter',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='structure_diameter', to='gwml2.Quantity', verbose_name='Diameter'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='material',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Material'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='reference_elevation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermReferenceElevationType', verbose_name='Reference elevation'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='top_depth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='structure_top_depth', to='gwml2.Quantity', verbose_name='Top depth'),
        ),
        migrations.AlterField(
            model_name='constructionstructure',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermConstructionStructureType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='drilling',
            name='cause_of_failure',
            field=models.TextField(blank=True, help_text='Explain why the drilling was not successful.', null=True, verbose_name='Cause of failure'),
        ),
        migrations.AlterField(
            model_name='drilling',
            name='driller',
            field=models.CharField(blank=True, help_text='Name of the drilling company or responsible person.', max_length=512, null=True, verbose_name='Contractor'),
        ),
        migrations.AlterField(
            model_name='drilling',
            name='drilling_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermDrillingMethod', verbose_name='Excavation method'),
        ),
        migrations.AlterField(
            model_name='drilling',
            name='successful',
            field=models.BooleanField(blank=True, null=True, verbose_name='Successful'),
        ),
        migrations.AlterField(
            model_name='drilling',
            name='year_of_drilling',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Construction year'),
        ),
        migrations.AlterField(
            model_name='geology',
            name='reference_elevation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermReferenceElevationType', verbose_name='Total depth reference elevation'),
        ),
        migrations.AlterField(
            model_name='geology',
            name='total_depth',
            field=models.OneToOneField(blank=True, help_text='Depth of the well below the ground surface.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Quantity', verbose_name='Total depth'),
        ),
        migrations.AlterField(
            model_name='hydrogeologyparameter',
            name='aquifer_material',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Aquifer material'),
        ),
        migrations.AlterField(
            model_name='hydrogeologyparameter',
            name='aquifer_name',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Aquifer name'),
        ),
        migrations.AlterField(
            model_name='hydrogeologyparameter',
            name='aquifer_thickness',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Aquifer thickness'),
        ),
        migrations.AlterField(
            model_name='hydrogeologyparameter',
            name='aquifer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermAquiferType', verbose_name='Aquifer type'),
        ),
        migrations.AlterField(
            model_name='hydrogeologyparameter',
            name='confinement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermConfinement', verbose_name='Confinement'),
        ),
        migrations.AlterField(
            model_name='hydrogeologyparameter',
            name='degree_of_confinement',
            field=models.FloatField(blank=True, null=True, verbose_name='Degree of confinement'),
        ),
        migrations.AlterField(
            model_name='license',
            name='description',
            field=models.TextField(blank=True, help_text='Explain what the license entails.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='license',
            name='number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Number'),
        ),
        migrations.AlterField(
            model_name='license',
            name='valid_from',
            field=models.DateField(blank=True, null=True, verbose_name='Valid from'),
        ),
        migrations.AlterField(
            model_name='license',
            name='valid_until',
            field=models.DateField(blank=True, null=True, verbose_name='Valid until'),
        ),
        migrations.AlterField(
            model_name='management',
            name='description',
            field=models.TextField(blank=True, help_text='Explain how the groundwater point is managed.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='management',
            name='groundwater_use',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermGroundwaterUse', verbose_name='Groundwater use'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='hydraulic_conductivity',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pumping_test_hydraulic_conductivity', to='gwml2.Quantity', verbose_name='Hydraulic conductivity'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='porosity',
            field=models.FloatField(blank=True, null=True, verbose_name='Porosity'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='specific_capacity',
            field=models.OneToOneField(blank=True, help_text='Specific capacity is the pumping rate divided by the drawdown. It gives an indication of the yield of a well.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pumping_test_specific_capacity', to='gwml2.Quantity', verbose_name='Specific capacity'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='specific_storage',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pumping_test_specific_storage', to='gwml2.Quantity', verbose_name='Specific storage'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='specific_yield',
            field=models.FloatField(blank=True, null=True, verbose_name='Specific yield'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='storativity',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pumping_test_storativity', to='gwml2.Quantity', verbose_name='Yield'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='test_type',
            field=models.CharField(blank=True, help_text='Provide information on the test(s) performed to estimate the hydraulic properties.', max_length=512, null=True, verbose_name='Test type'),
        ),
        migrations.AlterField(
            model_name='pumpingtest',
            name='transmissivity',
            field=models.OneToOneField(blank=True, help_text='Transmissivity is the hydraulic conductivity integrated over the thickness of the aquifer.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pumping_test_transmissivity', to='gwml2.Quantity', verbose_name='Transmissivity'),
        ),
        migrations.AlterField(
            model_name='stratigraphiclog',
            name='bottom_depth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stratigraphic_log_bottom_depth', to='gwml2.Quantity', verbose_name='Bottom depth'),
        ),
        migrations.AlterField(
            model_name='stratigraphiclog',
            name='material',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Material'),
        ),
        migrations.AlterField(
            model_name='stratigraphiclog',
            name='reference_elevation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermReferenceElevationType', verbose_name='Reference elevation'),
        ),
        migrations.AlterField(
            model_name='stratigraphiclog',
            name='stratigraphic_unit',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Stratigraphic unit'),
        ),
        migrations.AlterField(
            model_name='stratigraphiclog',
            name='top_depth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stratigraphic_log_top_depth', to='gwml2.Quantity', verbose_name='Top depth'),
        ),
        migrations.AlterField(
            model_name='waterstrike',
            name='depth',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Quantity', verbose_name='Depth'),
        ),
        migrations.AlterField(
            model_name='waterstrike',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='waterstrike',
            name='reference_elevation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermReferenceElevationType', verbose_name='Reference elevation'),
        ),
        migrations.AlterField(
            model_name='well',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='well',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='well',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='well',
            name='created_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='well',
            name='description',
            field=models.TextField(blank=True, help_text='A general description of the groundwater point.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='well',
            name='downloadable',
            field=models.BooleanField(default=True, help_text='Indicate that well can be downloaded.'),
        ),
        migrations.AlterField(
            model_name='well',
            name='feature_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermFeatureType', verbose_name='Feature type'),
        ),
        migrations.AlterField(
            model_name='well',
            name='ground_surface_elevation',
            field=models.OneToOneField(blank=True, help_text='Ground surface elevation above sea level.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ground_surface_elevation', to='gwml2.Quantity', verbose_name='Ground surface elevation'),
        ),
        migrations.AlterField(
            model_name='well',
            name='last_edited_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Last edited at'),
        ),
        migrations.AlterField(
            model_name='well',
            name='last_edited_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Last edited by'),
        ),
        migrations.AlterField(
            model_name='well',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(help_text='Location of the feature.', srid=4326, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='well',
            name='name',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='well',
            name='number_of_measurements',
            field=models.IntegerField(default=0, help_text='Indicate how many measurement this well has.'),
        ),
        migrations.AlterField(
            model_name='well',
            name='organisation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Organisation', verbose_name='Organisation'),
        ),
        migrations.AlterField(
            model_name='well',
            name='original_id',
            field=models.CharField(help_text='As recorded in the original database.', max_length=64, verbose_name='Original ID'),
        ),
        migrations.AlterField(
            model_name='well',
            name='photo',
            field=models.FileField(blank=True, help_text='A photo of the groundwater point. More photos can be added in annex.', null=True, upload_to='gwml2/photos/', verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='well',
            name='public',
            field=models.BooleanField(default=True, help_text='Indicate that well can be viewed by non organisation user.'),
        ),
        migrations.AlterField(
            model_name='well',
            name='purpose',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermWellPurpose', verbose_name='Purpose'),
        ),
        migrations.AlterField(
            model_name='well',
            name='restriction_code_type',
            field=models.IntegerField(blank=True, help_text='limitation(s) placed upon the access or use of the data. this is ID of restriction code in geonode.', null=True, verbose_name='Restrictions'),
        ),
        migrations.AlterField(
            model_name='well',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermWellStatus', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='well',
            name='top_borehole_elevation',
            field=models.OneToOneField(blank=True, help_text='Elevation of top of borehole above sea level.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='top_borehole_elevation', to='gwml2.Quantity', verbose_name='Top of well elevation'),
        ),
        migrations.AlterField(
            model_name='welldocument',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the feature.', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='welldocument',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='gwml2/document/', verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='welldocument',
            name='uploaded_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='Uploaded at'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='created_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='last_edited_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Last edited at'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='last_edited_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Last edited by'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='methodology',
            field=models.CharField(blank=True, help_text='Explain the methodology used to collect the data, in the field and eventually in the lab.', max_length=200, null=True, verbose_name='Methodology'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='parameter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermMeasurementParameter', verbose_name='Parameter'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Time'),
        ),
        migrations.AlterField(
            model_name='welllevelmeasurement',
            name='value',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Quantity', verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='created_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='last_edited_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Last edited at'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='last_edited_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Last edited by'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='methodology',
            field=models.CharField(blank=True, help_text='Explain the methodology used to collect the data, in the field and eventually in the lab.', max_length=200, null=True, verbose_name='Methodology'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='parameter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermMeasurementParameter', verbose_name='Parameter'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Time'),
        ),
        migrations.AlterField(
            model_name='wellqualitymeasurement',
            name='value',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Quantity', verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='created_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Created by'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='last_edited_at',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Last edited at'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='last_edited_by',
            field=models.IntegerField(blank=True, null=True, verbose_name='Last edited by'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='methodology',
            field=models.CharField(blank=True, help_text='Explain the methodology used to collect the data, in the field and eventually in the lab.', max_length=200, null=True, verbose_name='Methodology'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='parameter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.TermMeasurementParameter', verbose_name='Parameter'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Time'),
        ),
        migrations.AlterField(
            model_name='wellyieldmeasurement',
            name='value',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gwml2.Quantity', verbose_name='Value'),
        ),
    ]