import os
import shutil
import zipfile
from shutil import copyfile

from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import Q
from geonode.celery_app import app
from openpyxl import load_workbook

from gwml2.models.well import Well

logger = get_task_logger(__name__)

from gwml2.models.general import Country

GWML2_FOLDER = os.getenv(
    'GWML_FOLDER',
    os.path.join(settings.PROJECT_ROOT, 'gwml2-file')
)
DATA_FOLDER = os.path.join(GWML2_FOLDER, 'data')


def generate_downloadable_file(country: Country):
    DJANGO_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))

    wells = Well.objects.all()
    if country:
        wells = wells.filter(country=country)

    wells = wells.order_by('original_id')

    total_records = wells.count()

    # save it to media
    unique_id = country.code
    folder = os.path.join(DATA_FOLDER, str(unique_id))

    print(f'----- begin download : {unique_id}  -------')
    print('Found {} wells'.format(total_records))

    if os.path.exists(folder):
        shutil.rmtree(folder)

    os.makedirs(folder)

    # create file
    wells_filename = 'wells.xlsx'
    wells_file = os.path.join(folder, wells_filename)
    drilling_and_construction_filename = 'drilling_and_construction.xlsx'
    drilling_and_construction_file = os.path.join(
        folder, drilling_and_construction_filename)
    monitoring_filename = 'monitoring_data.xlsx'

    # copy template to actual folder
    copyfile(
        os.path.join(
            DJANGO_ROOT, 'gwml2', 'static', 'download_template',
            wells_filename),
        wells_file
    )
    copyfile(
        os.path.join(
            DJANGO_ROOT, 'gwml2', 'static', 'download_template',
            drilling_and_construction_filename),
        drilling_and_construction_file
    )

    monitoring_file = os.path.join(folder, monitoring_filename)
    copyfile(
        os.path.join(
            DJANGO_ROOT, 'gwml2', 'static', 'download_template',
            monitoring_filename),
        monitoring_file)

    # open sheets and start filling it
    start_index = 0
    step = 50
    end_index = step
    while start_index < total_records:
        well_book = load_workbook(wells_file)
        general_information_sheet = well_book['General Information']
        hydrogeology_sheet = well_book['Hydrogeology']
        management_sheet = well_book['Management']

        drilling_and_construction_book = load_workbook(
            drilling_and_construction_file)
        drilling_and_construction_sheet = drilling_and_construction_book[
            'Drilling and Construction']
        water_strike_sheet = drilling_and_construction_book['Water Strike']
        stratigraphic_sheet = drilling_and_construction_book[
            'Stratigraphic Log']
        structure_sheet = drilling_and_construction_book['Structures']

        # monitoring files
        process_percent = (start_index / total_records) * 100
        print(
            f'Progress : {process_percent}% '
            f'({start_index}/{total_records})'
        )
        for index, well in enumerate(wells[start_index:end_index]):
            # General Information
            general_information_sheet.append([
                well.original_id,
                well.name,
                well.feature_type.__str__() if well.feature_type else '',
                well.purpose.__str__() if well.purpose else '',
                well.status.__str__() if well.status else '',
                well.description,
                well.location.y,
                well.location.x,
                well.ground_surface_elevation.value if well.ground_surface_elevation else '',
                well.ground_surface_elevation.unit.name if well.ground_surface_elevation and well.ground_surface_elevation.unit else '',
                well.top_borehole_elevation.value if well.top_borehole_elevation else '',
                well.top_borehole_elevation.unit.name if well.top_borehole_elevation and well.top_borehole_elevation.unit else '',
                well.country.code if well.country else '',
                well.address,
            ])

            # drilling and construction
            drilling_and_construction_sheet.append([
                well.original_id,
                well.geology.total_depth.value if well.geology and well.geology.total_depth else '',
                well.geology.total_depth.unit.__str__() if well.geology and well.geology.total_depth and well.geology.total_depth.unit else '',
                well.drilling.drilling_method.__str__() if well.drilling and well.drilling.drilling_method else '',
                well.drilling.driller if well.drilling else '',
                (
                    'Yes' if well.drilling.successful else 'No') if well.drilling and well.drilling.successful is not None else '',
                well.drilling.cause_of_failure if well.drilling else '',
                well.drilling.year_of_drilling if well.drilling else '',
                well.construction.pump_installer if well.construction else '',
                well.construction.pump_description if well.construction else '',
            ])

            if well.drilling:
                # water strike
                for water_strike in well.drilling.waterstrike_set.all():
                    water_strike_sheet.append([
                        well.original_id,
                        water_strike.depth.value if water_strike.depth else '',
                        water_strike.depth.unit.__str__() if water_strike.depth and water_strike.depth.unit else '',
                        water_strike.reference_elevation.__str__() if water_strike.reference_elevation else ''
                    ])

                # stratigraphic
                for stratigraphiclog in well.drilling.stratigraphiclog_set.all():
                    stratigraphic_sheet.append([
                        well.original_id,
                        stratigraphiclog.reference_elevation.__str__() if stratigraphiclog.reference_elevation else '',
                        stratigraphiclog.top_depth.value if stratigraphiclog.top_depth else '',
                        stratigraphiclog.top_depth.unit.__str__() if stratigraphiclog.top_depth and stratigraphiclog.top_depth.unit else '',
                        stratigraphiclog.bottom_depth.value if stratigraphiclog.bottom_depth else '',
                        stratigraphiclog.bottom_depth.unit.__str__() if stratigraphiclog.top_depth and stratigraphiclog.bottom_depth.unit else '',
                        stratigraphiclog.material,
                        stratigraphiclog.stratigraphic_unit,
                    ])
            if well.construction:
                # structures
                for structure in well.construction.constructionstructure_set.all():
                    structure_sheet.append([
                        well.original_id,
                        structure.type.__str__() if structure.type else '',
                        structure.reference_elevation.__str__() if structure.reference_elevation else '',
                        structure.top_depth.value if structure.top_depth else '',
                        structure.top_depth.unit.__str__() if structure.top_depth and structure.top_depth.unit else '',
                        structure.bottom_depth.value if structure.bottom_depth else '',
                        structure.bottom_depth.unit.__str__() if structure.top_depth and structure.bottom_depth.unit else '',
                        structure.diameter.value if structure.diameter else '',
                        structure.diameter.unit.__str__() if structure.diameter and structure.diameter.unit else '',
                        structure.material,
                        structure.description
                    ])

            # Hydrogeology
            hydrogeology_sheet.append([
                well.original_id,
                well.hydrogeology_parameter.aquifer_name if well.hydrogeology_parameter else '',
                well.hydrogeology_parameter.aquifer_material if well.hydrogeology_parameter else '',
                well.hydrogeology_parameter.aquifer_type.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.aquifer_type else '',
                well.hydrogeology_parameter.aquifer_thickness if well.hydrogeology_parameter and well.hydrogeology_parameter.aquifer_thickness else '',
                well.hydrogeology_parameter.confinement.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.confinement else '',
                well.hydrogeology_parameter.degree_of_confinement if well.hydrogeology_parameter else '',

                well.hydrogeology_parameter.pumping_test.porosity if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test else '',

                # hydraulic conductivity
                well.hydrogeology_parameter.pumping_test.hydraulic_conductivity.value if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.hydraulic_conductivity else '',
                well.hydrogeology_parameter.pumping_test.hydraulic_conductivity.unit.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.hydraulic_conductivity and well.hydrogeology_parameter.pumping_test.hydraulic_conductivity.unit else '',

                # transmisivity
                well.hydrogeology_parameter.pumping_test.transmissivity.value if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.transmissivity else '',
                well.hydrogeology_parameter.pumping_test.transmissivity.unit.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.transmissivity and well.hydrogeology_parameter.pumping_test.transmissivity.unit else '',

                # specific storage
                well.hydrogeology_parameter.pumping_test.specific_storage.value if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.specific_storage else '',
                well.hydrogeology_parameter.pumping_test.specific_storage.unit.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.specific_storage and well.hydrogeology_parameter.pumping_test.specific_storage.unit else '',

                # specific capacity
                well.hydrogeology_parameter.pumping_test.specific_capacity.value if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.specific_capacity else '',
                well.hydrogeology_parameter.pumping_test.specific_capacity.unit.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.specific_capacity and well.hydrogeology_parameter.pumping_test.specific_capacity.unit else '',

                # specific capacity
                well.hydrogeology_parameter.pumping_test.storativity.value if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.storativity else '',
                well.hydrogeology_parameter.pumping_test.storativity.unit.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.storativity and well.hydrogeology_parameter.pumping_test.storativity.unit else '',

                well.hydrogeology_parameter.pumping_test.test_type if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test else '',
            ])

            # Management
            management_sheet.append([
                well.original_id,
                well.organisation.name if well.organisation else '',
                well.management.manager if well.management else '',
                well.management.description if well.management else '',
                well.management.groundwater_use.__str__() if well.management and well.management.groundwater_use else '',
                well.management.number_of_users if well.management else '',

                well.management.license.number if well.management and well.management.license else '',
                well.management.license.valid_from.strftime(
                    '%Y-%m-%d') if well.management and well.management.license and well.management.license.valid_from else '',
                well.management.license.valid_until.strftime(
                    '%Y-%m-%d') if well.management and well.management.license and well.management.license.valid_until else '',
                well.management.license.description if well.management and well.management.license else '',
            ])

            # Monitoring
            # LEVEL Measurement
            measurements = well.welllevelmeasurement_set.all()
            monitor_book = load_workbook(monitoring_file)
            sheets = monitor_book['Groundwater Level']
            for measurement in measurements:
                sheets.append([
                    well.original_id,
                    measurement.time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    measurement.parameter.__str__() if measurement.parameter else '',
                    measurement.value.value if measurement.value else '',
                    measurement.value.unit.name if measurement.value and measurement.value.unit else '',
                    measurement.methodology
                ])
            monitor_book.save(monitoring_file)

            # quality
            measurements = well.wellqualitymeasurement_set.all()
            monitor_book = load_workbook(monitoring_file)
            sheets = monitor_book['Groundwater Quality']
            for measurement in measurements:
                sheets.append([
                    well.original_id,
                    measurement.time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    measurement.parameter.__str__() if measurement.parameter else '',
                    measurement.value.value if measurement.value else '',
                    measurement.value.unit.name if measurement.value and measurement.value.unit else '',
                    measurement.methodology
                ])
            monitor_book.save(monitoring_file)

            # yield
            measurements = well.wellyieldmeasurement_set.all()
            monitor_book = load_workbook(monitoring_file)
            sheets = monitor_book['Abstraction-Discharge']
            for measurement in measurements:
                sheets.append([
                    well.original_id,
                    measurement.time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    measurement.parameter.__str__() if measurement.parameter else '',
                    measurement.value.value if measurement.value else '',
                    measurement.value.unit.name if measurement.value and measurement.value.unit else '',
                    measurement.methodology
                ])
            monitor_book.save(monitoring_file)

        well_book.save(wells_file)
        drilling_and_construction_book.save(drilling_and_construction_file)

        start_index = end_index
        end_index += step

    # -------------------------------------------------------------------------
    # zipping files
    # -------------------------------------------------------------------------
    zip_filename = '{}.zip'.format(str(unique_id))
    zip_file = os.path.join(DATA_FOLDER, zip_filename)
    if os.path.exists(zip_file):
        os.remove(zip_file)

    zip_file = zipfile.ZipFile(zip_file, 'w')
    zip_file.write(
        wells_file, wells_filename, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.write(
        drilling_and_construction_file,
        drilling_and_construction_filename,
        compress_type=zipfile.ZIP_DEFLATED)

    zip_file.write(
        monitoring_file, monitoring_filename,
        compress_type=zipfile.ZIP_DEFLATED)

    zip_file.close()
    shutil.rmtree(folder)
    return 'OK'


@app.task(
    bind=True,
    name='gwml2.tasks.well.generate_measurement_cache'
)
def generate_downloadable_file_cache(
        self, country: str = None, is_from: bool = False):
    countries = Country.objects.order_by('name')
    if country:
        try:
            country = countries.get(
                Q(name__iexact=country) | Q(code__iexact=country)
            )
            if not is_from:
                generate_downloadable_file(country)
            else:
                for country in countries.filter(name__gte=country.name):
                    generate_downloadable_file(country)
        except Country.DoesNotExist:
            print('Country not found')
    else:
        for country in countries:
            generate_downloadable_file(country)
