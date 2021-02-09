__author__ = 'Irwan Fathurrahman <meomancer@gmail.com>'
__date__ = '08/02/21'

import csv
import datetime
import json
import os
from django.contrib.auth import get_user_model
from gwml2.management.commands.fetch_from_ggmn import PARAMETER
from gwml2.models.well import Well
from gwml2.tasks.uploader.well import create_monitoring_data

User = get_user_model()


class NSGGMNData(object):
    """ GGMN N&S data """

    def __init__(self, fixture_folder):
        folder = os.path.join(
            fixture_folder, 'ggmn',
            'GGMN data N&S'
        )
        geojson = os.path.join(
            folder, 'IGRAC_groundwaterstations', 'IGRAC_groundwaterstations.geojson'
        )

        self.admin_id = User.objects.filter(
            is_superuser=True,
            username='admin'
        )[0].id

        # read geojson
        geojson_data_by_code = {}
        geojson_data_by_name = {}
        with open(geojson) as f:
            data = json.load(f)
            for feature in data['features']:
                properties = feature['properties']
                properties['geometry'] = feature['geometry']
                name = properties['name']
                code = properties['code']

                # save by code
                if code not in geojson_data_by_code:
                    geojson_data_by_code[code] = {}
                if name not in geojson_data_by_code[code]:
                    geojson_data_by_code[code][name] = properties
                else:
                    print('there is same code {} and name'.format(code, name))

                # save by name
                if name not in geojson_data_by_name:
                    geojson_data_by_name[name] = {}
                if code not in geojson_data_by_name[name]:
                    geojson_data_by_name[name][code] = properties
                else:
                    print('there is same name {} and code {}'.format(name, code))

        # lets check monitoring
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(root, file)) as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',')

                        csv_data_by_uuid = {}
                        monitoring_data_mode = False
                        dates = []
                        for row in csv_reader:
                            try:
                                if row[0] == 'uuid':
                                    continue
                                elif row[0] == 'name':
                                    monitoring_data_mode = True
                                    continue
                            except IndexError:
                                continue

                            if not monitoring_data_mode:
                                uuid = row[0]
                                parameter = row[1]
                                name = row[2]
                                x = row[3]
                                y = row[4]
                                if uuid in csv_data_by_uuid:
                                    print('there is duplicate uuid')
                                    continue
                                csv_data_by_uuid[uuid] = {
                                    'parameter': parameter,
                                    'code': name,
                                    'x': x,
                                    'y': y
                                }
                            else:
                                parameter = row[0]
                                uuid = row[1]
                                time = row[2]
                                value = row[3]
                                unit = 'm'
                                stasion_data = csv_data_by_uuid[uuid]
                                try:
                                    if not stasion_data['code']:
                                        continue
                                    geo_data = geojson_data_by_code[stasion_data['code']]
                                    if len(geo_data.keys()) > 1:
                                        print('There is multiple code')
                                    else:
                                        time_str = time
                                        if time_str in dates:
                                            continue
                                        time = datetime.datetime.strptime(
                                            time,
                                            '%d-%m-%Y'
                                        )

                                        row_data = [
                                            stasion_data['code'],  # ID
                                            time.strftime('%Y-%m-%d %H:%M:%S'),  # Date and time
                                            PARAMETER[parameter],  # Parameter
                                            value,  # Value
                                            unit,  # Unit
                                            '',  # Method
                                        ]
                                        create_monitoring_data(
                                            organisation_name=None,
                                            data=row_data,
                                            additional_data={
                                                'created_by': self.admin_id,
                                                'last_edited_by': self.admin_id
                                            },
                                        )
                                        dates.append(time_str)
                                except KeyError:
                                    print('Code {} not found in shapefile'.format(stasion_data['code']))
                                    print('File : {}'.format(os.path.join(root, file)))
                                except Well.DoesNotExist:
                                    pass
                                    # print('Well {} does not exist'.format(stasion_data['code']))
                                    # print('File : {}'.format(os.path.join(root, file)))
