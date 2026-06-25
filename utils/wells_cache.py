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
    ).values_list(
        'original_id', 'name',
        'time_str', 'parameter__name',
        'value__value', 'value__unit_id', 'value__unit__name',
        'depth_value', 'depth_unit__name',
        'methodology', 'time'
    ))

    # Write the file
    output = {"data": [], "page": 1, "end": True}
    for measurement in measurements:
        # Write to sheet file (For data download)
        # Exclude value__unit_id(5) and time(10) — not part of Excel format
        sheets.append((
            measurement[0], measurement[1], measurement[2], measurement[3],
            measurement[4], measurement[6], measurement[7], measurement[8],
            measurement[9]
        ))

        # Write to json file (For API)
        # measurement indices: original_id(0), name(1), time_str(2),
        # parameter__name(3), value__value(4), value__unit_id(5),
        # value__unit__name(6), depth_value(7), depth_unit__name(8),
        # methodology(9), time(10)
        value, result_unit_id = convert_value_by_id(
            measurement[4], measurement[5], unit_to_id,
            formula=unit_conversion_map.get(f'{measurement[5]},{unit_to_id}')
        )
        if value is None:
            continue

        unit = (
                   unit_to_name if result_unit_id == unit_to_id else
                   measurement[6]
               ) or ''
        parameter = measurement[3]

        if Model == WellLevelMeasurement:
            if parameter in [
                MEASUREMENT_PARAMETER_AMSL,
                MEASUREMENT_PARAMETER_TOP,
                MEASUREMENT_PARAMETER_GROUND
            ]:
                parameter = MEASUREMENT_PARAMETER_AMSL
                if measurement[3] == MEASUREMENT_PARAMETER_TOP:
                    if top_borehole_elevation and value > 0:
                        value = top_borehole_elevation.value - value
                    else:
                        parameter = measurement[3]
                elif measurement[3] == MEASUREMENT_PARAMETER_GROUND:
                    if ground_surface_elevation and value > 0:
                        value = ground_surface_elevation.value - value
                    else:
                        parameter = measurement[3]

        try:
            if round(value, 3) != 0:
                value = round(value, 3)
        except (TypeError, ValueError):
            pass

        output['data'].append({
            'dt': measurement[10].timestamp() if measurement[10] else None,
            'par': parameter,
            'u': unit,
            'v': value,
            'du': measurement[8] or '',
            'dv': measurement[7] or '',
        })

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