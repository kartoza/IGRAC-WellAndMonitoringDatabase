import json

from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus,
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.upload_session import UploadSession, UploadSessionRowStatus
from gwml2.models.well import (
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement
)
from gwml2.tasks.data_file_cache import generate_data_well_cache
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.uploader.well import get_column
from gwml2.tasks.well import generate_measurement_cache
from gwml2.utilities import temp_disconnect_signal
from gwml2.views.form_group.form_group import FormNotValid
from gwml2.views.groundwater_form import WellEditing

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

    status_column = {}

    def __init__(self, upload_session: UploadSession, restart: bool = False):
        from gwml2.signals.well import post_save_measurement_for_cache
        self.restart = restart
        self.upload_session = upload_session
        self.uploader = self.upload_session.get_uploader()
        _file = self.upload_session.upload_file
        _filename = _file.path

        self.upload_session.update_step('Reading file')
        self.total_records = 0
        self.relation_cache = {}

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

        # Disconnect
        with temp_disconnect_signal(
                signal=post_save,
                receiver=post_save_measurement_for_cache,
                sender=WellLevelMeasurement
        ):
            with temp_disconnect_signal(
                    signal=post_save,
                    receiver=post_save_measurement_for_cache,
                    sender=WellYieldMeasurement
            ):
                with temp_disconnect_signal(
                        signal=post_save,
                        receiver=post_save_measurement_for_cache,
                        sender=WellQualityMeasurement
                ):
                    self.process()

        # For report
        self.upload_session.update_step('Create report')
        self.upload_session.create_report_excel()

        # Finish
        self.upload_session.update_step('Finish')

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

        resumed_index = 0
        if not self.restart:
            try:
                status = json.loads(self.upload_session.status)
                resumed_index = status['added'] + status['error'] + status[
                    'skipped']
                progress = status
            except Exception:
                pass

        well_by_org = {}
        wells_id = []

        # ------------------------------
        # Upload data
        # ------------------------------
        self.upload_session.update_step('Upload data')
        index = 0
        for sheet_name, records in self.records.items():
            for row, raw_record in enumerate(records):
                index += 1
                if index <= resumed_index:
                    continue

                process_percent = (index / total_records) * 50

                # for saving records, 50%
                error = {}
                skipped = False
                well = None
                try:
                    original_id = get_column(raw_record, 0)
                    record = self._convert_record(sheet_name, raw_record)

                    well_identifier = f'{organisation.id}-{original_id}'
                    try:
                        try:
                            well = well_by_org[well_identifier]
                        except KeyError:
                            well = Well.objects.get(
                                organisation_id=organisation.id,
                                original_id=original_id
                            )
                            well_by_org[well_identifier] = well
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
                        well = self.update_data(well, record)
                        wells_id.append(well.id)
                except Well.DoesNotExist:
                    error = {
                        'original_id': 'Well does not exist'
                    }
                except TermNotFound as e:
                    error = json.loads('{}'.format(e))
                except FormNotValid as e:
                    error = json.loads('{}'.format(e))
                except Exception as e:
                    error = {
                        'original_id': '{}'.format(e)
                    }

                # ---------------------------------------------
                # Update progress and status
                # ---------------------------------------------
                row_idx = row + self.START_ROW + 1
                if error:
                    progress['error'] += 1

                    # create progress status per row
                    for key, note in error.items():
                        try:
                            column = list(self.RECORD_FORMAT.keys()).index(key)
                        except ValueError:
                            column = 0
                        if type(note) is list:
                            note = '<br>'.join(note)
                        obj, _ = UploadSessionRowStatus.objects.get_or_create(
                            upload_session=self.upload_session,
                            sheet_name=sheet_name,
                            row=row_idx,
                            column=column,
                            defaults={
                                'status': 1
                            }
                        )
                        obj.well = well
                        obj.status = 1
                        obj.note = note
                        obj.save()
                elif skipped:
                    progress['skipped'] += 1

                    # create progress status per row
                    obj, _ = UploadSessionRowStatus.objects.get_or_create(
                        upload_session=self.upload_session,
                        sheet_name=sheet_name,
                        row=row_idx,
                        column=0,
                        defaults={
                            'status': 2
                        }
                    )
                    obj.well = well
                    obj.status = 2
                    obj.save()
                else:
                    progress['added'] += 1

                    # create progress status per row
                    obj, _ = UploadSessionRowStatus.objects.get_or_create(
                        upload_session=self.upload_session,
                        sheet_name=sheet_name,
                        row=row_idx,
                        column=0,
                        defaults={
                            'status': 0
                        }
                    )
                    obj.well = well
                    obj.status = 0
                    obj.save()

                self.upload_session.update_progress(
                    progress=int(process_percent),
                    status=json.dumps(progress)
                )

        # ------------------------------------
        # Run the data cache
        # ------------------------------------
        self.upload_session.update_step('Running wells cache')
        wells_id = list(
            self.upload_session.uploadsessionrowstatus_set.values_list(
                'well_id', flat=True
            )
        )
        wells_id = list(set(wells_id))
        count = len(wells_id)
        for index, well_id in enumerate(wells_id):
            process_percent = ((index / count) * 25) + 50
            self.upload_session.update_progress(
                progress=int(process_percent),
                status=json.dumps(progress)
            )
            generate_measurement_cache(
                well_id=well_id, model=WellLevelMeasurement.__name__
            )
            generate_measurement_cache(
                well_id=well_id, model=WellYieldMeasurement.__name__
            )
            generate_measurement_cache(
                well_id=well_id, model=WellQualityMeasurement.__name__
            )
            generate_data_well_cache(
                well_id=well_id, generate_country_cache=False
            )

        # ------------------------------------
        # Run the country cache
        # ------------------------------------
        self.upload_session.update_step('Running country cache')
        countries_code = list(
            Well.objects.filter(
                id__in=wells_id
            ).values_list('country__code', flat=True)
        )
        countries_code = list(set(countries_code))
        count = len(countries_code)
        for index, country_code in enumerate(countries_code):
            process_percent = ((index / count) * 25) + 75
            self.upload_session.update_progress(
                progress=int(process_percent),
                status=json.dumps(progress)
            )
            generate_data_country_cache(country_code)

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
                    term_key = TERM.__name__
                    try:
                        cache = self.relation_cache[term_key]
                    except KeyError:
                        self.relation_cache[term_key] = {}
                        cache = self.relation_cache[term_key]
                    try:
                        value = cache[value]
                    except KeyError:
                        if TERM == Unit:
                            rel_value = TERM.objects.get(
                                name__iexact=value
                            ).name
                        else:
                            rel_value = TERM.objects.get(name__iexact=value).id
                        cache[value] = rel_value
                        value = rel_value
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
        """Convert record."""
        raise NotImplementedError

    def update_data(self, well, record) -> Well:
        """Process record"""
        raise NotImplementedError

    def get_object(self, sheet_name, well, record):
        """Return object that will be used."""
        raise NotImplementedError
