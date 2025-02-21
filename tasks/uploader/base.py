import json

from celery.utils.log import get_task_logger
from django.db.models import Q

from gwml2.models.general import Unit, Country
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus, TermGroundwaterUse
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.upload_session import (
    UploadSession, UploadSessionRowStatus
)
from gwml2.models.well import Well
from gwml2.tasks.uploader.well import get_column
from gwml2.utils.ods_reader import extract_data
from gwml2.utils.template_check import (
    compare_input_with_template, START_ROW
)
from gwml2.views.form_group.form_group import FormNotValid
from gwml2.views.groundwater_form import WellEditing

logger = get_task_logger(__name__)


class TermNotFound(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class RowSkipped(Exception):
    def __init__(self):
        super(Exception, self).__init__()


class BaseUploader(WellEditing):
    """ Convert excel into json and save the data """
    UPLOADER_NAME = ''
    IS_OPTIONAL = False
    SHEETS = []
    RECORD_FORMAT = {}
    AUTOCREATE_WELL = False

    # cache
    feature_types = {}
    purposes = {}
    status = {}
    units = {}
    organisations = {}
    groundwater_uses = {}
    aquifer_types = {}
    confinements = {}

    def __init__(
            self, upload_session: UploadSession,
            min_progress: int, interval_progress: int,
            restart: bool = False,
            well_by_id: dict = dict, relation_cache: dict = dict,
            file_path: str = None
    ):
        self.file_path = file_path
        self.min_progress = min_progress
        self.interval_progress = interval_progress

        self.well_by_id = well_by_id
        self.restart = restart
        self.upload_session = upload_session
        self.uploader = self.upload_session.get_uploader()
        self.relation_cache = relation_cache

        # cache
        self.feature_types = {}
        self.purposes = {}
        self.status = {}
        self.units = {}
        self.organisations = {}
        self.groundwater_uses = {}
        self.aquifer_types = {}
        self.confinements = {}
        self.records = {}

        self.records = {}
        self.current_index = 0
        self.current_row = 0
        self.resumed_index = None
        self.has_data = False

        # New approach
        self.upload_session.update_step('Processing data')
        self.process()

    def process(self):
        """ Process records """
        organisation = self.upload_session.organisation
        for sheet_name in self.SHEETS:
            self.current_row = 0
            self.resumed_index = None
            self.has_data = False

            progress = {
                'added': 0,
                'error': 0,
                'skipped': 0,
            }
            if not self.restart:
                try:
                    status = json.loads(
                        self.upload_session.status
                    )[sheet_name]
                    self.resumed_index = status[
                                             'added'
                                         ] + status[
                                             'error'
                                         ] + status[
                                             'skipped'
                                         ]
                    progress = status
                except Exception:
                    pass

            headers = []

            def receiver(raw_record):
                """This is for receiver"""
                if len(headers) < START_ROW:
                    headers.append(raw_record)

                    if len(headers) == START_ROW:
                        compare_input_with_template(
                            {sheet_name: headers},
                            sheet_name,
                            self.UPLOADER_NAME
                        )
                else:
                    self.has_data = True
                    self.current_row += 1

                    if len(raw_record) == 0:
                        return
                    if not raw_record[0]:
                        return
                    if (
                            self.resumed_index is not None
                            and self.current_row <= self.resumed_index
                    ):
                        return

                    self.current_index += 1

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
                            if not self.upload_session.is_adding:
                                raise RowSkipped()
                            if self.AUTOCREATE_WELL:
                                # This is for creating new data
                                well = None
                            else:
                                raise Well.DoesNotExist()

                        has_obj = self.get_object(sheet_name, well, record)
                        if not self.upload_session.is_updating and has_obj:
                            raise RowSkipped()

                        # Need to assign the data
                        if has_obj:
                            record = self.update_with_init_data(well, record)
                        # This is for updating data
                        well = self.update_data(well, record)
                    except Well.DoesNotExist:
                        error = {
                            'original_id': 'Well does not exist'
                        }
                    except TermNotFound as e:
                        error = json.loads('{}'.format(e))
                    except FormNotValid as e:
                        error = json.loads('{}'.format(e))
                    except RowSkipped:
                        skipped = True
                    except Exception as e:
                        error = {
                            'original_id': '{}'.format(e)
                        }

                    # ---------------------------------------------
                    # Update progress and status
                    # ---------------------------------------------
                    row_idx = self.current_row + START_ROW
                    if error:
                        progress['error'] += 1

                        # create progress status per row
                        for key, note in error.items():
                            try:
                                column = list(self.RECORD_FORMAT.keys()).index(
                                    key)
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

                    self.upload_session.update_step(
                        f'{sheet_name} : Row {row_idx}'
                    )
                    self.upload_session.update_status(sheet_name, progress)

            # Extract data per sheet
            extract_data(
                file_path=self.file_path,
                sheet_name=sheet_name,
                receiver=receiver
            )

            if not self.has_data and not self.IS_OPTIONAL:
                raise KeyError(
                    f'Sheet {sheet_name} in excel is not found. '
                    f'This sheet is used by {self.UPLOADER_NAME}. '
                    f'Please check if you use the correct uploader/tab. '
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
                        elif TERM == Country:
                            rel_value = TERM.objects.get(
                                Q(name__iexact=value) | Q(code__iexact=value)
                            ).id
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

    def update_with_init_data(self, well, record: dict):
        """Convert record."""
        return record

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
