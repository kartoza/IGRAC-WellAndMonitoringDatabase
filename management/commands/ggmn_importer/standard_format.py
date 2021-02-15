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


class StandardGGMNData(object):
    """ GGMN Standard data """

    def __init__(self, fixture_folder, file_name=None):
        folder = os.path.join(
            fixture_folder, 'ggmn',
            'Standard Format'
        )

        self.admin_id = User.objects.filter(
            is_superuser=True,
            username='admin'
        )[0].id

        # lets check monitoring
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(root, file)) as csv_file:
                        if file_name and file != file_name:
                            continue
                        print(file)

                        csv_reader = csv.reader(csv_file, delimiter=',')
                        dates = []
                        not_found = []
                        for row in csv_reader:
                            time = row[0]
                            parameter = row[1]
                            value = row[2]
                            original_id = row[3]
                            unit = 'm'
                            try:
                                if not original_id:
                                    continue

                                # skip if well is not found from before
                                if original_id in not_found:
                                    continue

                                try:
                                    time = datetime.datetime.strptime(
                                        time,
                                        '%Y-%m-%dT%H:%M:%SZ'
                                    )
                                except TypeError:
                                    pass

                                str_time = time.strftime('%Y-%m-%d %H:%M:%S')
                                identifer = '{}-{}'.format(original_id, str_time)
                                if identifer in dates:
                                    continue

                                row_data = [
                                    original_id,  # ID
                                    str_time,  # Date and time
                                    PARAMETER[parameter],  # Parameter
                                    value,  # Value
                                    unit,  # Unit
                                    '',  # Method
                                ]
                                wells = Well.objects.filter(
                                    original_id=original_id).order_by('-number_of_measurements')
                                if wells.count() > 1:
                                    print('Well {} has duplication'.format(original_id))
                                    print('File : {}'.format(os.path.join(root, file)))
                                elif wells.count() == 0:
                                    raise Well.DoesNotExist

                                create_monitoring_data(
                                    organisation_name=None,
                                    data=row_data,
                                    additional_data={
                                        'created_by': self.admin_id,
                                        'last_edited_by': self.admin_id
                                    },
                                    well=wells[0]
                                )
                                dates.append(identifer)
                            except KeyError:
                                print('Code {} not found in shapefile'.format(original_id))
                                print('File : {}'.format(os.path.join(root, file)))
                            except Well.DoesNotExist:
                                not_found.append(original_id)
                                print('Well {} does not exist'.format(original_id))
                                print('File : {}'.format(os.path.join(root, file)))
