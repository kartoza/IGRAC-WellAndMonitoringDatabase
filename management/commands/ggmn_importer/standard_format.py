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

    def __init__(self, fixture_folder):
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
                        csv_reader = csv.reader(csv_file, delimiter=',')

                        dates = []
                        for row in csv_reader:
                            time = row[0]
                            parameter = row[1]
                            value = row[2]
                            original_id = row[3]
                            unit = 'm'
                            try:
                                if not original_id:
                                    continue
                                time_str = time
                                if time_str in dates:
                                    continue
                                time = datetime.datetime.strptime(
                                    time,
                                    '%Y-%m-%dT%H:%M:%SZ'
                                )

                                row_data = [
                                    original_id,  # ID
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
                                print('Code {} not found in shapefile'.format(original_id))
                                print('File : {}'.format(os.path.join(root, file)))
                            except Well.DoesNotExist:
                                print('Well {} does not exist'.format(original_id))
                                print('File : {}'.format(os.path.join(root, file)))
