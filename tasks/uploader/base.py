import json

from celery.utils.log import get_task_logger

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus, TermGroundwaterUse
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.upload_session import UploadSession, UploadSessionRowStatus
from gwml2.models.well import (
    Well
)
from gwml2.tasks.uploader.well import get_column
from gwml2.views.form_group.form_group import FormNotValid
from gwml2.views.groundwater_form import WellEditing

logger = get_task_logger(__name__)


class TermNotFound(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class BaseUploader(WellEditing):
    """ Convert excel into json and save the data """
    UPLOADER_NAME = ''
    IS_OPTIONAL = False
    SHEETS = []
    START_ROW = 2
    RECORD_FORMAT = {}
    AUTOCREATE_WELL = False

    def __init__(
            self, upload_session: UploadSession, records: dict,
            min_progress: int, interval_progress: int,
            restart: bool = False,
            well_by_id: dict = dict, relation_cache: dict = dict
    ):
        self.min_progress = min_progress
        self.interval_progress = interval_progress

        self.well_by_id = well_by_id
        self.restart = restart
        self.upload_session = upload_session
        self.uploader = self.upload_session.get_uploader()
        self.relation_cache = relation_cache

        self.total_records = 0
        self.records = {}
        try:
            for sheet_name in self.SHEETS:
                sheet_records = records[sheet_name][self.START_ROW:]
                self.records[sheet_name] = sheet_records
                self.total_records += len(sheet_records)
        except KeyError as e:
            if self.IS_OPTIONAL:
                return
            error = (
                f'Sheet {e} in excel is not found. '
                f'This sheet is used by {self.UPLOADER_NAME}. '
                f'Please check if you use the correct uploader/tab. '
            )

            self.upload_session.update_progress(
                finished=True,
                progress=100,
                status=error
            )
            return

        self.process()

    def process(self):
        """ Process records """
        organisation = self.upload_session.organisation
        total = self.total_records

        logger.debug('Found {} wells'.format(total))

        # ------------------------------
        # Upload data
        # ------------------------------
        index = 0
        for sheet_name, records in self.records.items():
            progress = {
                'added': 0,
                'error': 0,
                'skipped': 0,
            }

            resumed_index = 0
            if not self.restart:
                try:
                    status = json.loads(
                        self.upload_session.status
                    )[sheet_name]
                    resumed_index = status['added'] + status['error'] + status[
                        'skipped']
                    progress = status
                except Exception:
                    pass

            for row, raw_record in enumerate(records):
                if row + 1 <= resumed_index:
                    continue
                if len(raw_record) == 0:
                    continue

                index += 1
                curr_progress = (index / total) * self.interval_progress
                process_percent = curr_progress + self.min_progress

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
                            well = self.well_by_id[well_identifier]
                        except KeyError:
                            well = Well.objects.get(
                                organisation_id=organisation.id,
                                original_id=original_id
                            )
                            self.well_by_id[well_identifier] = well
                    except Well.DoesNotExist:
                        if self.AUTOCREATE_WELL:
                            well = None
                        else:
                            raise Well.DoesNotExist()

                    # TODO:
                    #  just remove this if the data is allowed to be updated
                    if self.get_object(sheet_name, well, record):
                        skipped = True
                    else:
                        well = self.update_data(well, record)
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
                    progress=int(process_percent)
                )
                self.upload_session.update_status(sheet_name, progress)

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
                except TermGroundwaterUse.DoesNotExist:
                    raise TermNotFound(json.dumps(
                        {key: 'Groundwater use does not exist'}
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
        return self.edit_well(
            well, record, {},
            self.uploader,
            generate_cache=False
        )

    def get_object(self, sheet_name, well, record):
        """Return object that will be used."""
        raise NotImplementedError
