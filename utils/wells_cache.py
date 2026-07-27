import gzip
import json
import os

from django.db.models import Value, CharField, Func

from gwml2.models import (
    Well, WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_AMSL, MEASUREMENT_PARAMETER_TOP,
    MEASUREMENT_PARAMETER_GROUND
)
from gwml2.utilities import convert_value_by_id

MEASUREMENT_MODELS = [
    WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
]

MeasurementModel = (
        type[WellLevelMeasurement]
        | type[WellQualityMeasurement]
        | type[WellYieldMeasurement]
)


def generate_measurement_data_cache(
        well: Well,
        sheets,
        Model: MeasurementModel,
        unit_conversion_map: dict,
        ground_surface_elevation,
        top_borehole_elevation,
        unit_to_id,
        unit_to_name,
):
    """Measurements cache of well.

     It generate for excel for data download and json for API."""
    # ----------------- measurements api ------------------
    json_filename = well.return_measurement_cache_path(Model.__name__)

    # depth_value/depth_unit only exist on WellQualityMeasurement.
    has_depth = Model == WellQualityMeasurement

    fields = [
        'original_id', 'name', 'time_str', 'parameter__name',
        'value__value', 'value__unit_id', 'value__unit__name',
    ]
    if has_depth:
        fields += ['depth_value', 'depth_unit__name']
    fields += ['methodology', 'time']

    original_id = well.original_id
    measurements = list(Model.objects.filter(well=well).annotate(
        original_id=Value(original_id, output_field=CharField()),
        name=Value(well.name, output_field=CharField()),
        time_str=Func(
            'time',
            Value('YYYY-MM-DD HH24:MI:SS'),
            function='to_char',
            output_field=CharField()
        )
    ).values(*fields))

    # Write the file
    output = {"data": [], "page": 1, "end": True}
    for measurement in measurements:
        # Write to sheet file (For data download)
        # Exclude value__unit_id and time — not part of Excel format
        row = [
            measurement['original_id'], measurement['name'],
            measurement['time_str'], measurement['parameter__name'],
            measurement['value__value'], measurement['value__unit__name'],
        ]
        if has_depth:
            row += [
                measurement['depth_value'], measurement['depth_unit__name']
            ]
        row.append(measurement['methodology'])
        sheets.append(tuple(row))

        # Write to json file (For API)
        value, result_unit_id = convert_value_by_id(
            measurement['value__value'], measurement['value__unit_id'],
            unit_to_id,
            formula=unit_conversion_map.get(
                f"{measurement['value__unit_id']},{unit_to_id}"
            )
        )
        if value is None:
            continue

        unit = (
                   unit_to_name if result_unit_id == unit_to_id else
                   measurement['value__unit__name']
               ) or ''
        parameter = measurement['parameter__name']

        if Model == WellLevelMeasurement:
            if parameter in [
                MEASUREMENT_PARAMETER_AMSL,
                MEASUREMENT_PARAMETER_TOP,
                MEASUREMENT_PARAMETER_GROUND
            ]:
                parameter = MEASUREMENT_PARAMETER_AMSL
                if measurement['parameter__name'] == MEASUREMENT_PARAMETER_TOP:
                    if top_borehole_elevation and value > 0:
                        value = top_borehole_elevation.value - value
                    else:
                        parameter = measurement['parameter__name']
                elif measurement['parameter__name'] == MEASUREMENT_PARAMETER_GROUND:
                    if ground_surface_elevation and value > 0:
                        value = ground_surface_elevation.value - value
                    else:
                        parameter = measurement['parameter__name']

        try:
            if round(value, 3) != 0:
                value = round(value, 3)
        except (TypeError, ValueError):
            pass

        data_row = {
            'dt': (
                measurement['time'].timestamp()
                if measurement['time'] else None
            ),
            'par': parameter,
            'u': unit,
            'v': value,
        }
        if has_depth:
            data_row['du'] = measurement['depth_unit__name'] or ''
            data_row['dv'] = measurement['depth_value'] or ''
        output['data'].append(data_row)

    # Save to json
    # Remove the file
    if os.path.exists(json_filename):
        os.remove(json_filename)

    # If it has output data, write to file
    try:
        if output['data']:
            os.makedirs(os.path.dirname(json_filename), exist_ok=True)
            json_str = json.dumps(output) + "\n"
            json_bytes = json_str.encode('utf-8')
            file = gzip.open(json_filename, 'wb', compresslevel=1)
            file.write(json_bytes)
            file.close()
    except KeyError:
        pass