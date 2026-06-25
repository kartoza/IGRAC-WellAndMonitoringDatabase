import os
import zipfile
from decimal import Decimal
from xml.sax.saxutils import escape as xml_escape

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


_ROW_OPEN = b'<table:table-row table:style-name="ro4">'
_ROW_CLOSE = b'</table:table-row>'
_CELL_EMPTY = b'<table:table-cell table:style-name="ce3"/>'
_CELL_FLOAT_A = b'<table:table-cell table:style-name="ce3" office:value-type="float" office:value="'
_CELL_FLOAT_B = b'"><text:p>'
_CELL_FLOAT_C = b'</text:p></table:table-cell>'
_CELL_STR_A = b'<table:table-cell table:style-name="ce3" office:value-type="string"><text:p>'
_CELL_STR_B = b'</text:p></table:table-cell>'


def _build_raw_rows_bytes(buffer):
    """Build buffered rows as raw UTF-8 bytes for direct injection into XML."""
    parts = []
    extend = parts.extend
    append = parts.append
    for row_data in buffer:
        append(_ROW_OPEN)
        for value in row_data:
            if value is None or value == '':
                append(_CELL_EMPTY)
            elif isinstance(value, (int, float, Decimal)):
                v = str(value).encode()
                extend((_CELL_FLOAT_A, v, _CELL_FLOAT_B, v, _CELL_FLOAT_C))
            else:
                v = xml_escape(str(value)).encode('utf-8')
                extend((_CELL_STR_A, v, _CELL_STR_B))
        append(_ROW_CLOSE)
    return b''.join(parts)


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

        # Parse the small template and place a unique marker comment after
        # each sheet's anchor row — avoids parsing the large data XML later.
        root = etree.fromstring(content_xml)
        tables = {
            t.get(ATTR_TABLE_NAME): t
            for t in root.findall('.//{%s}table' % NS_TABLE)
        }
        insertions = {}
        for sheet_name, wrapper in self._sheets.items():
            if not wrapper._buffer:
                continue
            table = tables.get(sheet_name)
            if table is None:
                continue
            rows = table.findall('{%s}table-row' % NS_TABLE)
            anchor = rows[1] if len(rows) > 1 else rows[0]
            marker = f'IGRAC_INSERT_{id(wrapper)}'
            anchor.addnext(etree.Comment(marker))
            insertions[marker.encode()] = wrapper._buffer

        # Serialize the template (still small — only header rows + markers).
        template_bytes = etree.tostring(
            root, xml_declaration=True, encoding='UTF-8', standalone=True
        )

        # Replace each marker with raw row bytes — no XML parsing needed.
        new_content = template_bytes
        for marker_bytes, buffer in insertions.items():
            rows_bytes = _build_raw_rows_bytes(buffer)
            new_content = new_content.replace(
                b'<!--' + marker_bytes + b'-->', rows_bytes
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
                    dst.writestr(info, new_content, compresslevel=1)
                else:
                    dst.writestr(info, data)
        os.replace(tmp_path, target)

    def close(self):
        self._sheets.clear()
