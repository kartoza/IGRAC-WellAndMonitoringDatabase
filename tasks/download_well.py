import uuid
import os

from django.conf import settings
from django.http import JsonResponse
from collections import OrderedDict
from pyexcel_xlsx import save_data

from celery import shared_task
from celery.utils.log import get_task_logger
from gwml2.models.well import Well
from gwml2.tasks.controller import update_progress

logger = get_task_logger(__name__)


@shared_task(bind=True, queue='update')
def download_well(self, filters=None):
    logger.debug('----- begin download  -------')
    if filters:
        # TODO :
        #  implement filters
        wells = Well.objects.filter()
    else:
        wells = Well.objects.all()
    total_records = wells.count()
    logger.debug('Found {} wells'.format(total_records))

    # headers
    informations = [
        [
            'Original ID', 'Status', 'Feature Type', 'Purpose', 'Description',
            'Latitude', 'Longitude', 'Ground surface elevation', 'Top borehole elevation', 'Country', 'Address',  # Information
        ]
    ]
    drilling_construction = [
        [
            'Total Depth', 'Drilling Method', 'Driller', 'Successful', 'Cause of failure ', 'Year of drilling',  # Drilling
            'Pump Construction', 'Pump Description'  # Construction
        ]
    ]
    hydrogeology = [
        [
            'Aquifer name', 'Aquifer material', 'Aquifer type', 'Aquifer thickness', 'Confinement', 'Degree of confinement',  # Aquifer
            'Porosity', 'Hydraulic conductivity', 'Transmissivity', 'Specific storage', 'Specific capacity', 'Storativity', 'Test type'  # Hydraulic properties
        ]
    ]
    management = [
        [
            'Manager / Owner', 'Management Description',
            'Groundwater use', 'Number of people served',  # Production
            'Number', 'Valid from', 'Valid until', 'License Description'  # License
        ]
    ]
    for index, well in enumerate(wells):
        process_percent = (index / total_records) * 100
        update_progress(process_percent)

        # append data
        informations.append([
            well.original_id,
            well.status.__str__() if well.status else '',
            well.feature_type.__str__() if well.feature_type else '',
            well.purpose.__str__() if well.purpose else '',
            well.description,

            # information
            well.location.y,
            well.location.x,
            well.ground_surface_elevation.__str__() if well.ground_surface_elevation else '',
            well.top_borehole_elevation.__str__() if well.top_borehole_elevation else '',
            well.country.__str__() if well.country else '',
            well.address,
        ])

        drilling_construction.append([
            well.drilling.total_depth.__str__() if well.drilling and well.drilling.total_depth else '',
            well.drilling.drilling_method.__str__() if well.drilling and well.drilling.drilling_method else '',
            well.drilling.driller if well.drilling else '',
            well.drilling.successful if well.drilling else '',
            well.drilling.cause_of_failure if well.drilling else '',
            well.drilling.year_of_drilling if well.drilling else '',

            # pump
            well.construction.pump_installer if well.construction else '',
            well.construction.pump_description if well.construction else '',
        ])

        hydrogeology.append([
            # Aquifer
            well.hydrogeology_parameter.aquifer_name if well.hydrogeology_parameter else '',
            well.hydrogeology_parameter.aquifer_material if well.hydrogeology_parameter else '',
            well.hydrogeology_parameter.aquifer_type.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.aquifer_type else '',
            well.hydrogeology_parameter.aquifer_thickness.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.aquifer_thickness else '',
            well.hydrogeology_parameter.confinement.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.confinement else '',
            well.hydrogeology_parameter.degree_of_confinement if well.hydrogeology_parameter else '',

            # Hydraulic properties
            well.hydrogeology_parameter.pumping_test.porosity if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test else '',
            well.hydrogeology_parameter.pumping_test.hydraulic_conductivity.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.hydraulic_conductivity else '',
            well.hydrogeology_parameter.pumping_test.transmissivity.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.transmissivity else '',
            well.hydrogeology_parameter.pumping_test.specific_storage.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.specific_storage else '',
            well.hydrogeology_parameter.pumping_test.specific_capacity.__str__() if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test and well.hydrogeology_parameter.pumping_test.specific_capacity else '',
            well.hydrogeology_parameter.pumping_test.storativity if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test else '',
            well.hydrogeology_parameter.pumping_test.test_type if well.hydrogeology_parameter and well.hydrogeology_parameter.pumping_test else '',
        ])

        management.append([
            well.management.manager if well.management else '',
            well.management.groundwater_use.__str__() if well.management and well.management.groundwater_use else '',
            well.management.description if well.management else '',
            well.management.number_of_users if well.management else '',

            # license
            well.management.license.number if well.management and well.management.license else '',
            well.management.license.valid_from.strftime('%Y-%m-%d') if well.management and well.management.license and well.management.license.valid_from else '',
            well.management.license.valid_until.strftime('%Y-%m-%d') if well.management and well.management.license and well.management.license.valid_until else '',
            well.management.license.description if well.management and well.management.license else '',

        ])

    data = OrderedDict()
    data.update({"Information": informations})
    data.update({"Drilling and Construction": drilling_construction})
    data.update({"Hydrogeology": hydrogeology})
    data.update({"Management": management})

    # save it to media
    MEDIA_ROOT = settings.MEDIA_ROOT
    folder = os.path.join(MEDIA_ROOT, 'gwml2', 'download')
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = '{}.xlsx'.format(str(uuid.uuid4()))
    file = os.path.join(folder, filename)
    save_data(file, data)

    MEDIA_URL = settings.MEDIA_URL
    url = os.path.join(MEDIA_URL, 'gwml2', 'download', filename)

    update_progress(100, {
        'url': url
    })
    return JsonResponse({'status': 'success'})
