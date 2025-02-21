"""Check template data."""

import copy
import os

from django.conf import settings
from pyexcel_ods3 import get_data

START_ROW = 2


def get_records(
        sheets: list, records: dict, uploader_name: str
) -> (dict, int):
    """Get data from records."""
    try:
        total_records = 0
        output = {}
        for sheet_name in sheets:
            try:
                sheet_records = records[sheet_name][START_ROW:]
            except KeyError:
                _sheet_name = sheet_name.replace(' ', '_')
                sheet_records = records[_sheet_name][START_ROW:]

            # Compare the file
            compare_input_with_template(records, sheet_name, uploader_name)

            # Update output
            output[sheet_name] = sheet_records
            total_records += len(sheet_records)
        return output, total_records
    except KeyError as e:
        raise KeyError(
            f'Sheet {e} in excel is not found. '
            f'This sheet is used by {uploader_name}. '
            f'Please check if you use the correct uploader/tab. '
        )


def compare_input_with_template(records: dict, sheet_name: str, uploader_name):
    """Compare input with the template."""
    from gwml2.tasks.data_file_cache.wells_cache import TEMPLATE_FOLDER
    try:
        headers = records[sheet_name][:START_ROW]
    except KeyError:
        _sheet_name = sheet_name.replace(' ', '_')
        headers = records[_sheet_name][:START_ROW]
    headers = copy.deepcopy(headers)

    if uploader_name.lower() == 'General Information'.lower():
        uploader_name = 'wells'

    template_records = get_data(
        os.path.join(
            TEMPLATE_FOLDER,
            f'{uploader_name.replace(" ", "_").lower()}.ods'
        )
    )
    try:
        template_headers = template_records[
                               sheet_name.replace(' ', '_')
                           ][:START_ROW]
    except KeyError:
        _sheet_name = sheet_name.replace('_', ' ')
        template_headers = template_records[_sheet_name][:START_ROW]
    template_headers = copy.deepcopy(template_headers)

    # update headers
    for idx, row in enumerate(headers):
        remove_last_empty_element(row)
        for idx_cell, cell in enumerate(row):
            headers[idx][idx_cell] = cell.strip().replace(
                '\n', '').replace(' ', '').replace('•', '').replace(
                '  (READ ONLY)', '(READ ONLY)'
            )

    # Update template header
    for idx, row in enumerate(template_headers):
        for idx_cell, cell in enumerate(row):
            template_headers[idx][idx_cell] = cell.strip().replace(
                ' ', '').replace('\n', '').replace('•', '').replace(
                '  (READ ONLY)', '(READ ONLY)'
            )
    if template_headers != headers:
        raise ValueError(
            'The file is out of date, '
            'please download the latest template on the form'
        )


def remove_last_empty_element(row):
    """Remove last empty elements."""
    stop = False
    _len = len(row)
    for i, item in enumerate(reversed(row)):
        if item:
            stop = True
        if not stop and not item:
            del row[_len - 1 - i]


def compare_ods_xlsx_template(xlsx_filename, uploader_name):
    """Compare ods and xlsx template."""
    xlsx_filename = os.path.join(
        settings.STATIC_ROOT,
        'download_template',
        xlsx_filename
    )
    ods_records = get_data(xlsx_filename)
    for key, rows in ods_records.items():
        for idx, row in enumerate(rows[:START_ROW]):
            prev = ''
            for idx_cell, cell in enumerate(row):
                if prev and cell == prev:
                    ods_records[key][idx][idx_cell] = ''
                prev = cell

            remove_last_empty_element(row)
    try:
        get_records(
            ods_records.keys(), ods_records, uploader_name
        )
        return True
    except ValueError:
        return False
