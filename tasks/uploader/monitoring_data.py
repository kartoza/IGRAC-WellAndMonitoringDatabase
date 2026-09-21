import json

from celery.utils.log import get_task_logger
from django.db import transaction

from gwml2.models.general import Quantity, Unit, UnitConvertion
from gwml2.models.measurement import Measurement
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.upload_session import UploadSessionRowStatus
from gwml2.models.well import (
    Well,
    WellLevelMeasurement,
    WellQualityMeasurement,
    WellYieldMeasurement,
)
from gwml2.tasks.uploader.base import BaseUploader
from gwml2.tasks.uploader.well import get_column
from gwml2.terms import SheetName
from gwml2.utilities import parse_float, parse_time
from gwml2.utils.ods_reader import extract_data
from gwml2.utils.template_check import START_ROW, compare_input_with_template

logger = get_task_logger(__name__)


class MonitoringDataUploader(BaseUploader):
    """Save well monitoring measurements from excel, in bulk batches.

    Bypasses `edit_well()`/Django forms; writes via bulk_create/
    bulk_update instead, replicating `value_in_m`/`default_value`
    manually since those bulk ops skip model save() signals.
    """

    UPLOADER_NAME = "Monitoring Data"
    BATCH_SIZE = 5000

    MODEL_BY_SHEET = {
        SheetName.groundwater_level: WellLevelMeasurement,
        SheetName.groundwater_quality: WellQualityMeasurement,
        SheetName.abstraction_discharge: WellYieldMeasurement,
    }
    SHEETS = list(MODEL_BY_SHEET.keys())
    HAS_DEPTH_SHEET = SheetName.groundwater_quality
    WELL_FLAG_FIELD = {
        SheetName.groundwater_level: "is_groundwater_level",
        SheetName.groundwater_quality: "is_groundwater_quality",
    }

    def get_fields(self, sheet_name):
        """Column names in file order for this sheet."""
        if sheet_name == self.HAS_DEPTH_SHEET:
            return [
                "original_id",
                "name",
                "time",
                "parameter",
                "value_value",
                "value_unit",
                "depth_value",
                "depth_unit",
                "methodology",
            ]
        return [
            "original_id",
            "name",
            "time",
            "parameter",
            "value_value",
            "value_unit",
            "methodology",
        ]

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def process(self):
        """Process every sheet using batched bulk writes."""
        self._units_by_name = {unit.name.lower(): unit for unit in Unit.objects.all()}
        self._parameters_by_name = {
            param.name.lower(): param for param in TermMeasurementParameter.objects.all()
        }
        self._unit_conversions = {
            (c.unit_from_id, c.unit_to_id): c.formula for c in UnitConvertion.objects.all()
        }

        for sheet_name in self.SHEETS:
            self.upload_session.update_step(f"{sheet_name} : Reading data")
            self._process_sheet(sheet_name)

    def _get_saved_progress(self, sheet_name):
        try:
            status = json.loads(self.upload_session.status)[sheet_name]
            return {
                "added": status.get("added", 0),
                "error": status.get("error", 0),
                "skipped": status.get("skipped", 0),
            }
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Sheet-level orchestration: streamed, batch-at-a-time
    # ------------------------------------------------------------------
    def _process_sheet(self, sheet_name):
        """Read a sheet and process it batch-by-batch as rows come in."""
        resumed_index = 0
        progress = {"added": 0, "error": 0, "skipped": 0}
        if not self.restart:
            saved_progress = self._get_saved_progress(sheet_name)
            if saved_progress:
                resumed_index = (
                    saved_progress["added"] + saved_progress["error"] + saved_progress["skipped"]
                )
                progress = saved_progress

        fields = self.get_fields(sheet_name)
        headers = []
        rows = []  # list of (row_number, row_dict)
        current_row = 0
        affected_wells = set()

        def receiver(raw_record):
            nonlocal current_row

            # Check row if it is header
            if len(headers) < START_ROW:
                headers.append(raw_record)

                # We compare ods with template
                if len(headers) == START_ROW:
                    compare_input_with_template(
                        {sheet_name: headers}, sheet_name, self.UPLOADER_NAME
                    )
                return

            # If current is not resumed index
            current_row += 1
            if current_row <= resumed_index:
                return

            if not get_column(raw_record, 0):
                return

            # Convert to a named dict here
            row = {field: get_column(raw_record, idx) for idx, field in enumerate(fields)}
            rows.append((current_row + START_ROW, row))
            if len(rows) >= self.BATCH_SIZE:
                process_rows()

        def process_rows():
            nonlocal rows
            if not rows:
                return

            first_row = rows[0][0]
            last_row = rows[-1][0]
            self.upload_session.update_step(
                f"{sheet_name} : Processing Row {first_row}"
            )
            affected_wells.update(self._process_batch(sheet_name, rows, progress))
            self.upload_session.update_step(
                f"{sheet_name} : Row {first_row} to {last_row} done"
            )
            self.upload_session.update_status(sheet_name, progress)
            rows = []

        extract_data(file_path=self.file_path, sheet_name=sheet_name, receiver=receiver)
        process_rows()

        # Update flags
        flag_field = self.WELL_FLAG_FIELD.get(sheet_name)
        if flag_field and affected_wells:
            Well.objects.filter(
                id__in=affected_wells, **{f"{flag_field}__in": [None, "no"]}
            ).update(**{flag_field: "yes"})

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------
    def _process_batch(self, sheet_name, rows, progress):
        model = self.MODEL_BY_SHEET[sheet_name]
        candidates, skipped, row_errors = self._parse_batch(sheet_name, rows)

        candidate_well_ids = {c["well"].id for c in candidates}
        candidate_times = {c["time"] for c in candidates}
        candidate_parameter_ids = {c["parameter"].id for c in candidates}
        existing = self._preload_existing(
            model, candidate_well_ids, candidate_times, candidate_parameter_ids
        )

        to_insert = []
        to_update = []
        affected_wells = set()

        for c in candidates:
            key = (c["well"].id, c["time"], c["parameter"].id)
            match = existing.get(key)
            if match is None:
                if self.upload_session.is_adding:
                    to_insert.append(c)
                    affected_wells.add(c["well"].id)
                else:
                    skipped.append(c)
            elif self.upload_session.is_updating:
                c["existing_pk"], c["existing_value_id"] = match
                to_update.append(c)
                affected_wells.add(c["well"].id)
            else:
                skipped.append(c)

        self._write_batch(sheet_name, to_insert, to_update)
        self._write_row_statuses(sheet_name, progress, to_insert, to_update, skipped, row_errors)
        return affected_wells

    def _parse_batch(self, sheet_name, rows):
        """Resolve wells/units/parameters for a batch's rows."""
        organisation = self.upload_session.organisation
        has_depth = sheet_name == self.HAS_DEPTH_SHEET
        # Column index per field, needed only to report which cell an
        # error belongs to (UploadSessionRowStatus.column is an int).
        col = {name: idx for idx, name in enumerate(self.get_fields(sheet_name))}

        original_ids = {row["original_id"] for _, row in rows}
        original_ids.discard(None)
        original_ids.discard("")

        wells_by_key = {}
        if organisation:
            for well in Well.objects.filter(
                organisation_id=organisation.id, original_id__in=original_ids
            ):
                wells_by_key.setdefault((well.original_id, well.name), []).append(well)

        candidates = []
        skipped_no_well = []
        row_errors = []

        for row_number, row in rows:
            original_id = row["original_id"]
            name = row["name"]
            errors = {}
            well = None

            try:
                # Per row, get the well
                well_matches = wells_by_key.get((original_id, name), [])
                if len(well_matches) == 1:
                    well = well_matches[0]
                elif len(well_matches) > 1:
                    errors[col["original_id"]] = f"Found {len(well_matches)} wells for this ID/name"

                # If well and not errors
                if well is None and col["original_id"] not in errors:
                    if self.upload_session.is_adding:
                        errors[col["original_id"]] = "Well does not exist"
                    else:
                        skipped_no_well.append(
                            {
                                "row_number": row_number,
                                "well": None,
                            }
                        )
                        continue

                # Time check
                time_value = parse_time(row["time"])
                if time_value is None:
                    errors[col["time"]] = "Time is required and must be valid"

                # Parameter check
                parameter_name = row["parameter"]
                parameter = self._parameters_by_name.get((parameter_name or "").strip().lower())
                if not parameter_name:
                    errors[col["parameter"]] = "Parameter is required"
                elif not parameter:
                    errors[col["parameter"]] = "Parameter does not exist"

                # Value check
                raw_value = row["value_value"]
                value = parse_float(raw_value)
                if raw_value not in (None, "") and value is None:
                    errors[col["value_value"]] = "Value must be a number"

                # Unit check
                unit_name = row["value_unit"]
                unit = None
                if unit_name:
                    unit = self._units_by_name.get(unit_name.strip().lower())
                    if not unit:
                        errors[col["value_unit"]] = "Unit does not exist"

                # Depth check
                depth_value = depth_unit = None
                if has_depth:
                    raw_depth_value = row["depth_value"]
                    depth_value = parse_float(raw_depth_value)
                    if raw_depth_value not in (None, "") and depth_value is None:
                        errors[col["depth_value"]] = "Depth value must be a number"
                    depth_unit_name = row["depth_unit"]
                    if depth_unit_name:
                        depth_unit = self._units_by_name.get(depth_unit_name.strip().lower())
                        if not depth_unit:
                            errors[col["depth_unit"]] = "Depth unit does not exist"
            except Exception as e:
                errors[col["original_id"]] = str(e)

            if errors:
                row_errors.append((row_number, well, errors))
                continue

            candidates.append(
                {
                    "row_number": row_number,
                    "well": well,
                    "time": time_value,
                    "parameter": parameter,
                    "value": value,
                    "unit": unit,
                    "depth_value": depth_value,
                    "depth_unit": depth_unit,
                    "methodology": row["methodology"],
                }
            )

        return candidates, skipped_no_well, row_errors

    def _apply_derived_fields(self, sheet_name, candidate):
        """Fill in default_value/default_unit (+ value_in_m) in place."""
        is_level_measurement = sheet_name == SheetName.groundwater_level
        candidate.update(
            Measurement.apply_derived_fields(
                candidate, is_level_measurement, self._unit_conversions
            )
        )

    @staticmethod
    def _preload_existing(model, well_ids, times, parameter_ids):
        """Map (well_id, time, parameter_id) -> (pk, value_id).

        Narrowed by time/parameter too (not just well_id) so wells with a
        long measurement history don't pull back far more rows than this
        batch could ever match.
        """
        if not well_ids:
            return {}
        return {
            (well_id, time_value, parameter_id): (pk, value_id)
            for well_id, time_value, parameter_id, pk, value_id in model.objects.filter(
                well_id__in=well_ids, time__in=times, parameter_id__in=parameter_ids
            ).values_list("well_id", "time", "parameter_id", "id", "value_id")
        }

    @transaction.atomic
    def _write_batch(self, sheet_name, to_insert, to_update):
        """bulk_create new rows, bulk_update conflicting ones."""
        self._write_inserts(sheet_name, to_insert)
        self._write_updates(sheet_name, to_update)

    def _write_inserts(self, sheet_name, to_insert):
        if not to_insert:
            return
        model = self.MODEL_BY_SHEET[sheet_name]
        for candidate in to_insert:
            self._apply_derived_fields(sheet_name, candidate)

        quantities = [Quantity(value=c["value"], unit=c["unit"]) for c in to_insert]
        Quantity.objects.bulk_create(quantities, batch_size=self.BATCH_SIZE)
        for candidate, quantity in zip(to_insert, quantities):
            candidate["quantity_id"] = quantity.id

        model.objects.bulk_create(
            [self._build_instance(sheet_name, c) for c in to_insert],
            batch_size=self.BATCH_SIZE,
        )

    def _write_updates(self, sheet_name, to_update):
        if not to_update:
            return
        model = self.MODEL_BY_SHEET[sheet_name]
        has_depth = sheet_name == self.HAS_DEPTH_SHEET

        for candidate in to_update:
            self._apply_derived_fields(sheet_name, candidate)

        update_fields = ["value", "methodology", "default_value", "default_unit"]
        if model is WellLevelMeasurement:
            update_fields.append("value_in_m")
        if has_depth:
            update_fields += ["depth_value", "depth_unit"]

        def build_update_instances(cands):
            instances = []
            for c in cands:
                instance = self._build_instance(sheet_name, c)
                instance.pk = c["existing_pk"]
                instances.append(instance)
            return instances

        has_quantity = [c for c in to_update if c.get("existing_value_id")]
        needs_quantity = [c for c in to_update if not c.get("existing_value_id")]

        if has_quantity:
            quantity_updates = [
                Quantity(pk=c["existing_value_id"], value=c["value"], unit=c["unit"])
                for c in has_quantity
            ]
            Quantity.objects.bulk_update(
                quantity_updates, ["value", "unit"], batch_size=self.BATCH_SIZE
            )
            for c in has_quantity:
                c["quantity_id"] = c["existing_value_id"]

            model.objects.bulk_update(
                build_update_instances(has_quantity), update_fields, batch_size=self.BATCH_SIZE
            )

        if needs_quantity:
            quantities = [Quantity(value=c["value"], unit=c["unit"]) for c in needs_quantity]
            Quantity.objects.bulk_create(quantities, batch_size=self.BATCH_SIZE)
            for c, quantity in zip(needs_quantity, quantities):
                c["quantity_id"] = quantity.id

            model.objects.bulk_update(
                build_update_instances(needs_quantity), update_fields, batch_size=self.BATCH_SIZE
            )

    def _build_instance(self, sheet_name, candidate):
        model = self.MODEL_BY_SHEET[sheet_name]
        kwargs = dict(
            well=candidate["well"],
            time=candidate["time"],
            parameter=candidate["parameter"],
            methodology=candidate["methodology"],
            value_id=candidate["quantity_id"],
            default_value=candidate["default_value"],
            default_unit_id=candidate["default_unit_id"],
        )
        if model is WellLevelMeasurement:
            kwargs["value_in_m"] = candidate["value_in_m"] or 0.0
        if sheet_name == self.HAS_DEPTH_SHEET:
            kwargs["depth_value"] = candidate["depth_value"]
            kwargs["depth_unit"] = candidate["depth_unit"]
        return model(**kwargs)

    def _write_row_statuses(self, sheet_name, progress, to_insert, to_update, skipped, row_errors):
        statuses = []
        for c in to_insert + to_update:
            progress["added"] += 1
            statuses.append(
                UploadSessionRowStatus(
                    upload_session=self.upload_session,
                    sheet_name=sheet_name,
                    row=c["row_number"],
                    column=0,
                    status=0,
                    well=c["well"],
                )
            )
        for c in skipped:
            progress["skipped"] += 1
            statuses.append(
                UploadSessionRowStatus(
                    upload_session=self.upload_session,
                    sheet_name=sheet_name,
                    row=c["row_number"],
                    column=0,
                    status=2,
                    well=c.get("well"),
                )
            )
        for row_number, well, errors in row_errors:
            progress["error"] += 1
            for column, note in errors.items():
                statuses.append(
                    UploadSessionRowStatus(
                        upload_session=self.upload_session,
                        sheet_name=sheet_name,
                        row=row_number,
                        column=column,
                        status=1,
                        note=note,
                        well=well,
                    )
                )

        if statuses:
            UploadSessionRowStatus.objects.bulk_create(
                statuses, batch_size=self.BATCH_SIZE, ignore_conflicts=True
            )
