"""Tests for OdsDoc / OdsSheetWrapper (ods_writer.py)."""
import os.path
import shutil
import tempfile
import zipfile
from decimal import Decimal

from lxml import etree

from core.settings.utils import absolute_path
from gwml2.tests.base import GWML2Test
from gwml2.utils.ods_reader import extract_data, get_count
from gwml2.utils.ods_writer import EXCEL_MAX_ROWS, NS_TABLE, OdsDoc

TEMPLATE_PATH = absolute_path(
    'gwml2', 'static', 'download_template', 'monitoring_data.ods'
)

SHEET_LEVEL = 'Groundwater Level'
SHEET_QUALITY = 'Groundwater Quality'
SHEET_YIELD = 'Abstraction-Discharge'

ROW_LEVEL = (
    'W001', 'Well A', '2024-01-01 00:00:00',
    'Water depth', 5.0, 'm', None, None, 'Manual'
)
ROW_QUALITY = (
    'W001', 'Well A', '2024-01-01 00:00:00',
    'EC', 100.0, 'S/m', None, None, ''
)
ROW_YIELD = (
    'W001', 'Well A', '2024-01-01 00:00:00',
    'Abstraction', 50.0, 'm³/h', None, None, ''
)


def _read_rows(ods_path, sheet_name):
    """Read data rows from a saved ODS using extract_data."""
    rows = []
    extract_data(ods_path, sheet_name, rows.append)
    return rows


def _total_row_count(ods_path, sheet_name):
    """Sum table-row repeat counts for one sheet (its real grid height)."""
    with zipfile.ZipFile(ods_path) as zf:
        content = zf.read('content.xml')
    root = etree.fromstring(content)
    total = 0
    for table in root.findall('.//{%s}table' % NS_TABLE):
        if table.get('{%s}name' % NS_TABLE) != sheet_name:
            continue
        for row in table.findall('{%s}table-row' % NS_TABLE):
            repeated = row.get('{%s}number-rows-repeated' % NS_TABLE)
            total += int(repeated) if repeated else 1
    return total


class OdsWriterTest(GWML2Test):
    """Tests for OdsDoc and OdsSheetWrapper."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.ods_path = f'{self.tmp_dir}/monitoring_data.ods'
        shutil.copy(TEMPLATE_PATH, self.ods_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_append_single_row(self):
        doc = OdsDoc(self.ods_path)
        doc[SHEET_LEVEL].append(ROW_LEVEL)
        doc.save()

        original_rows = _read_rows(TEMPLATE_PATH, SHEET_LEVEL)
        rows = _read_rows(self.ods_path, SHEET_LEVEL)
        self.assertEqual(len(original_rows), 2)
        self.assertEqual(original_rows[0], rows[0])
        self.assertEqual(original_rows[1], rows[1])

        self.assertEqual(len(rows), 3)
        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 1)
        self.assertEqual(rows[2][0], 'W001')
        self.assertEqual(rows[2][1], 'Well A')

    def test_append_multiple_rows_preserves_order(self):
        doc = OdsDoc(self.ods_path)
        sheet = doc[SHEET_LEVEL]
        for i in range(1, 4):
            sheet.append(
                (
                    f'W{i:03d}', f'Well {i}', '2024-01-01 00:00:00',
                    'Water depth', float(i), 'm', None, None, ''
                )
            )
        doc.save()

        rows = _read_rows(self.ods_path, SHEET_LEVEL)
        self.assertEqual(len(rows), 5)
        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 3)
        self.assertEqual(rows[2][0], 'W001')
        self.assertEqual(rows[3][0], 'W002')
        self.assertEqual(rows[4][0], 'W003')

    def test_none_values_produce_empty_cells(self):
        doc = OdsDoc(self.ods_path)
        doc[SHEET_LEVEL].append(
            (
                'W001', None, '2024-01-01 00:00:00',
                None, 1.0, 'm', None, None, None
            )
        )
        doc.save()

        rows = _read_rows(self.ods_path, SHEET_LEVEL)
        self.assertEqual(len(rows), 3)
        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 1)
        self.assertEqual(rows[2][1], '')
        self.assertEqual(rows[2][3], '')

    def test_numeric_decimal_written_correctly(self):
        doc = OdsDoc(self.ods_path)
        doc[SHEET_LEVEL].append(
            (
                'W001', 'Well A', '2024-01-01 00:00:00',
                'Water depth', Decimal('3.14'), 'm', None, None, ''
            )
        )
        doc.save()

        rows = _read_rows(self.ods_path, SHEET_LEVEL)
        self.assertEqual(len(rows), 3)
        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 1)
        self.assertEqual(rows[2][4], '3.14')

    def test_all_three_sheets_written(self):
        doc = OdsDoc(self.ods_path)
        doc[SHEET_LEVEL].append(ROW_LEVEL)
        doc[SHEET_QUALITY].append(ROW_QUALITY)
        doc[SHEET_YIELD].append(ROW_YIELD)
        doc.save()

        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 1)
        self.assertEqual(get_count(self.ods_path, SHEET_QUALITY), 1)
        self.assertEqual(get_count(self.ods_path, SHEET_YIELD), 1)

    def test_empty_sheet_has_no_data_rows(self):
        doc = OdsDoc(self.ods_path)
        doc[SHEET_LEVEL]  # access without appending
        doc.save()

        rows = _read_rows(self.ods_path, SHEET_LEVEL)
        self.assertEqual(len(rows), 2)
        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 0)

    def test_row_count_stays_within_excel_limit(self):
        """Appended rows must not push the total past Excel's row limit."""
        baseline = _total_row_count(TEMPLATE_PATH, SHEET_LEVEL)
        self.assertEqual(baseline, EXCEL_MAX_ROWS)

        doc = OdsDoc(self.ods_path)
        sheet = doc[SHEET_LEVEL]
        for i in range(500):
            sheet.append(
                (
                    f'W{i:05d}', 'Well', '2024-01-01 00:00:00',
                    'Water depth', 1.0, 'm', None, None, ''
                )
            )
        doc.save()

        total = _total_row_count(self.ods_path, SHEET_LEVEL)
        self.assertLessEqual(total, EXCEL_MAX_ROWS)
        self.assertEqual(total, baseline)

    def test_same_sheet_reference_returned(self):
        doc = OdsDoc(self.ods_path)
        self.assertIs(doc[SHEET_LEVEL], doc[SHEET_LEVEL])

    def test_row_count_matches_appended(self):
        doc = OdsDoc(self.ods_path)
        sheet = doc[SHEET_LEVEL]
        for i in range(10):
            sheet.append(
                (
                    f'W{i:03d}', 'Well', '2024-01-01 00:00:00',
                    'Water depth', float(i), 'm', None, None, ''
                )
            )
        doc.save()

        rows = _read_rows(self.ods_path, SHEET_LEVEL)
        self.assertEqual(len(rows), 12)
        self.assertEqual(get_count(self.ods_path, SHEET_LEVEL), 10)
