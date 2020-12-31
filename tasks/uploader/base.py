import json
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from celery.utils.log import get_task_logger

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus,
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import Well
from gwml2.models.upload_session import UploadSession
from gwml2.views.form_group.form_group import FormNotValid
from gwml2.views.groundwater_form import WellEditing
from gwml2.tasks.uploader.well import get_column

logger = get_task_logger(__name__)


class TermNotFound(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class BaseUploader(WellEditing):
    """ Convert excel into json and save the data """
    AUTOCREATE_WELL = False
    SHEETS = []
    START_ROW = 2
    RECORD_FORMAT = {}
    WELL_AUTOCREATE = False

    def __init__(self, upload_session: UploadSession):
        self.upload_session = upload_session
        _file = self.upload_session.upload_file

        self.total_records = 0
        records = {}
        if _file:
            _file.seek(0)
            sheet = None
            if str(_file).split('.')[-1] == 'xls':
                sheet = xls_get(_file, column_limit=20)
            elif str(_file).split('.')[-1] == 'xlsx':
                sheet = xlsx_get(_file, column_limit=20)
            if sheet:
                try:
                    for sheet_name in self.SHEETS:
                        sheet_records = sheet[sheet_name][self.START_ROW:]
                        records[sheet_name] = sheet_records
                        self.total_records += len(sheet_records)
                except KeyError as e:
                    self.upload_session.update_progress(
                        finished=True,
                        progress=100,
                        status='Sheet {} is needed'.format(e)
                    )
                    return
        self.records = records
        self.process()

    def process(self):
        """ Process records """
        organisation = self.upload_session.organisation
        total_records = self.total_records
        logger.debug('Found {} wells'.format(total_records))

        progress = {
            'added': 0,
            'error': 0,
            'skipped': 0,
        }
        index = 0
        for sheet_name, records in self.records.items():
            for raw_record in records:
                index += 1
                process_percent = (index / total_records) * 100
                error = {}
                skipped = False
                try:
                    original_id = get_column(raw_record, 0)
                    record = self._convert_record(sheet_name, raw_record)

                    try:
                        well = Well.objects.get(
                            organisation=organisation, original_id=original_id
                        )
                    except Well.DoesNotExist:
                        if self.WELL_AUTOCREATE:
                            well = None
                        else:
                            raise Well.DoesNotExist()

                    # TODO:
                    #  just remove this if the data is allowed to be updated
                    if self.get_object(sheet_name, well, record):
                        skipped = True
                    else:
                        self.edit_well(well, record, {}, self.upload_session.get_uploader())
                except Well.DoesNotExist:
                    error = {
                        'original_id': 'well does not exist'
                    }
                except TermNotFound as e:
                    error = json.loads('{}'.format(e))
                except FormNotValid as e:
                    error = json.loads('{}'.format(e))
                except Exception as e:
                    error = '{}'.format(e)

                # update progress
                if error:
                    progress['error'] += 1
                elif skipped:
                    progress['skipped'] += 1
                else:
                    progress['added'] += 1

                self.upload_session.update_progress(
                    progress=int(process_percent),
                    status=json.dumps(progress)
                )

        # finish
        self.upload_session.update_progress(
            finished=True,
            progress=100,
            status=json.dumps(progress)
        )

    def _convert_record(self, sheet_name, record):
        """ convert record into json data
        :return: dictionary of forms
        :rtype: dict
        """
        data = {}
        for index, key in enumerate(self.RECORD_FORMAT.keys()):
            value = get_column(
                record,
                index
            )
            TERM = self.RECORD_FORMAT[key]
            if value and TERM:
                try:
                    if TERM == Unit:
                        value = TERM.objects.get(name__iexact=value).name
                    else:
                        value = TERM.objects.get(name__iexact=value).id
                except TermFeatureType.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Feature Type does not exist'}
                    ))
                except TermWellPurpose.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Purpose does not exist'}
                    ))
                except TermWellStatus.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Status does not exist'}
                    ))
                except Unit.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Unit does not exist'}
                    ))
                except Country.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Country does not exist'}
                    ))
                except TermMeasurementParameter.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Parameter does not exist'}
                    ))
                except KeyError:
                    pass
            data[key] = value

        return self.convert_record(sheet_name, data)

    def convert_record(self, sheet_name, data):
        """ return object that will be used
        """
        raise NotImplementedError

    def get_object(self, sheet_name, well, record):
        """ return object that will be used
        """
        raise NotImplementedError
