import os
import zipfile
from decimal import Decimal

from lxml import etree

NS_TABLE = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
NS_OFFICE = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
NS_TEXT = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'

TAG_ROW = '{%s}table-row' % NS_TABLE
TAG_CELL = '{%s}table-cell' % NS_TABLE
TAG_P = '{%s}p' % NS_TEXT
ATTR_VALUE_TYPE = '{%s}value-type' % NS_OFFICE
ATTR_VALUE = '{%s}value' % NS_OFFICE
ATTR_TABLE_NAME = '{%s}name' % NS_TABLE
ATTR_STYLE_NAME = '{%s}style-name' % NS_TABLE

DATA_CELL_STYLE = 'ce3'
DATA_ROW_STYLE = 'ro4'


def _build_cell(value):
    cell = etree.Element(TAG_CELL)
    cell.set(ATTR_STYLE_NAME, DATA_CELL_STYLE)
    if value is None or value == '':
        return cell
    if isinstance(value, (int, float, Decimal)):
        cell.set(ATTR_VALUE_TYPE, 'float')
        cell.set(ATTR_VALUE, str(value))
        p = etree.SubElement(cell, TAG_P)
        p.text = str(value)
    else:
        cell.set(ATTR_VALUE_TYPE, 'string')
        p = etree.SubElement(cell, TAG_P)
        p.text = str(value)
    return cell


def _build_row(row_data):
    row_el = etree.Element(TAG_ROW)
    row_el.set(ATTR_STYLE_NAME, DATA_ROW_STYLE)
    for value in row_data:
        row_el.append(_build_cell(value))
    return row_el


class OdsSheetWrapper:
    """Buffers rows in memory; flushed to XML on OdsDoc.save()."""

    def __init__(self, name):
        self.name = name
        self._buffer = []

    def append(self, row_data):
        self._buffer.append(row_data)


class OdsDoc:
    """
    Loads an ODS template and injects data rows using lxml + zipfile,
    bypassing ezodf's per-cell XML overhead.
    """

    def __init__(self, path):
        self._path = path
        self._sheets = {}

    def __getitem__(self, sheet_name):
        if sheet_name not in self._sheets:
            self._sheets[sheet_name] = OdsSheetWrapper(sheet_name)
        return self._sheets[sheet_name]

    def save(self, path=None):
        target = path or self._path
        with zipfile.ZipFile(self._path) as z:
            content_xml = z.read('content.xml')
            all_files = {
                info.filename: (info, z.read(info.filename))
                for info in z.infolist()
            }

        root = etree.fromstring(content_xml)
        tables = {
            t.get(ATTR_TABLE_NAME): t
            for t in root.findall('.//{%s}table' % NS_TABLE)
        }

        for sheet_name, wrapper in self._sheets.items():
            if not wrapper._buffer:
                continue
            table = tables.get(sheet_name)
            if table is None:
                continue

            # Find the 2nd header row to insert after
            rows = table.findall('{%s}table-row' % NS_TABLE)
            anchor = rows[1] if len(rows) > 1 else rows[0]

            # addnext in O(1) per row — keeps a running tail pointer
            prev = anchor
            for row_data in wrapper._buffer:
                new_row = _build_row(row_data)
                prev.addnext(new_row)
                prev = new_row

        new_content = etree.tostring(
            root, xml_declaration=True, encoding='UTF-8', standalone=True
        )

        tmp_path = target + '.tmp'
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as dst:
            for filename, (info, data) in all_files.items():
                if filename == 'mimetype':
                    dst.writestr(
                        zipfile.ZipInfo('mimetype'), data,
                        compress_type=zipfile.ZIP_STORED
                    )
                elif filename == 'content.xml':
                    dst.writestr(info, new_content)
                else:
                    dst.writestr(info, data)
        os.replace(tmp_path, target)

    def close(self):
        self._sheets.clear()
