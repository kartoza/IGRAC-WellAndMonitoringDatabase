"""Direct, in-place editor for existing ODS spreadsheets.

Edits specific (sheet, row, column) cells of an ODS file that already
contains data -- setting a value and/or a style -- without converting
through xlsx and back via an external `soffice` process.

ODS compresses runs of identical rows/cells using
`table:number-rows-repeated` / `table:number-columns-repeated`. Any
repeated block that is touched gets split into individual elements so the
edit only affects the exact logical row/column addressed; everything else
stays compressed as-is.
"""
import copy
import os
import zipfile

from lxml import etree

from gwml2.utils.ods_reader import is_correct_sheet

NS_TABLE = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
NS_OFFICE = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
NS_TEXT = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
NS_STYLE = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
NS_FO = 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'


def _q(ns, tag):
    return '{%s}%s' % (ns, tag)


TAG_TABLE = _q(NS_TABLE, 'table')
TAG_ROW = _q(NS_TABLE, 'table-row')
TAG_CELL = _q(NS_TABLE, 'table-cell')
TAG_COVERED_CELL = _q(NS_TABLE, 'covered-table-cell')
TAG_P = _q(NS_TEXT, 'p')
TAG_AUTOMATIC_STYLES = _q(NS_OFFICE, 'automatic-styles')
TAG_STYLE = _q(NS_STYLE, 'style')
TAG_CELL_PROPS = _q(NS_STYLE, 'table-cell-properties')
TAG_TEXT_PROPS = _q(NS_STYLE, 'text-properties')

ATTR_TABLE_NAME = _q(NS_TABLE, 'name')
ATTR_ROWS_REPEATED = _q(NS_TABLE, 'number-rows-repeated')
ATTR_COLS_REPEATED = _q(NS_TABLE, 'number-columns-repeated')
ATTR_STYLE_NAME = _q(NS_TABLE, 'style-name')
ATTR_VALUE_TYPE = _q(NS_OFFICE, 'value-type')
ATTR_STYLE_NAME_DEF = _q(NS_STYLE, 'name')
ATTR_STYLE_FAMILY = _q(NS_STYLE, 'family')
ATTR_BG_COLOR = _q(NS_FO, 'background-color')
ATTR_FONT_COLOR = _q(NS_FO, 'color')


def _get_repeat(el, attr):
    value = el.get(attr)
    return int(value) if value else 1


def _set_repeat(el, attr, count):
    if count <= 1:
        el.attrib.pop(attr, None)
    else:
        el.set(attr, str(count))


def _locate_indexed(parent, count_tags, target_tag, repeat_attr, index):
    """Return the `target_tag` child at 1-based logical `index`.

    `count_tags` are the tags that occupy a logical slot (e.g. both
    table-cell and covered-table-cell occupy a column), while only
    `target_tag` can actually be split off and returned/edited. Splits
    the repeated block containing `index`, mutating `parent` in place.
    """
    cursor = 0
    for child in list(parent):
        if child.tag not in count_tags:
            continue
        repeat = _get_repeat(child, repeat_attr)
        if cursor + repeat >= index:
            if child.tag != target_tag:
                raise ValueError(
                    f'Logical index {index} is covered by a '
                    f'<{etree.QName(child).localname}> element and '
                    f'cannot be edited directly'
                )
            offset = index - cursor
            if repeat == 1:
                return child

            before_count = offset - 1
            after_count = repeat - offset
            insert_pos = list(parent).index(child)

            target_el = copy.deepcopy(child)
            _set_repeat(target_el, repeat_attr, 1)
            after_el = None
            if after_count > 0:
                after_el = copy.deepcopy(child)
                _set_repeat(after_el, repeat_attr, after_count)

            if before_count > 0:
                _set_repeat(child, repeat_attr, before_count)
                parent.insert(insert_pos + 1, target_el)
                if after_el is not None:
                    parent.insert(insert_pos + 2, after_el)
            else:
                parent.remove(child)
                parent.insert(insert_pos, target_el)
                if after_el is not None:
                    parent.insert(insert_pos + 1, after_el)
            return target_el
        cursor += repeat
    raise IndexError(
        f'Logical index {index} out of range (found {cursor} entries)'
    )


class OdsCellStyle:
    """A registrable table-cell automatic style: background + font color."""

    def __init__(self, name, background=None, font_color=None):
        self.name = name
        self.background = background
        self.font_color = font_color

    def build_element(self):
        style = etree.Element(TAG_STYLE)
        style.set(ATTR_STYLE_NAME_DEF, self.name)
        style.set(ATTR_STYLE_FAMILY, 'table-cell')
        cell_props = etree.SubElement(style, TAG_CELL_PROPS)
        if self.background:
            cell_props.set(ATTR_BG_COLOR, self.background)
        if self.font_color:
            text_props = etree.SubElement(style, TAG_TEXT_PROPS)
            text_props.set(ATTR_FONT_COLOR, self.font_color)
        return style


class OdsEditor:
    """Loads an existing ODS file for in-place, random-access cell edits."""

    def __init__(self, path):
        self._path = path
        with zipfile.ZipFile(path) as z:
            self._files = {
                info.filename: (info, z.read(info.filename))
                for info in z.infolist()
            }
        self._root = etree.fromstring(self._files['content.xml'][1])
        self._tables = {
            t.get(ATTR_TABLE_NAME): t
            for t in self._root.findall('.//%s' % TAG_TABLE)
        }
        self._automatic_styles = self._root.find(TAG_AUTOMATIC_STYLES)
        if self._automatic_styles is None:
            self._automatic_styles = etree.SubElement(
                self._root, TAG_AUTOMATIC_STYLES
            )
        self._registered_styles = set()

    def sheet_names(self):
        """Return the sheet (table) names in this document."""
        return list(self._tables.keys())

    def _table(self, sheet_name):
        table = self._tables.get(sheet_name)
        if table is not None:
            return table
        for name, table in self._tables.items():
            if is_correct_sheet(name, sheet_name):
                return table
        raise KeyError(f'Sheet "{sheet_name}" not found')

    def register_style(self, style: OdsCellStyle):
        """Register a cell style so it can be referenced by name."""
        if style.name in self._registered_styles:
            return
        self._automatic_styles.append(style.build_element())
        self._registered_styles.add(style.name)

    def header_columns(self, sheet_name):
        """Yield (1-based column index, has_value) for row 1 of a sheet.

        Read-only -- does not split repeated blocks, since nothing here
        is being edited.
        """
        table = self._table(sheet_name)
        rows = [c for c in table if c.tag == TAG_ROW]
        if not rows:
            return
        cursor = 0
        for cell in rows[0]:
            if cell.tag not in (TAG_CELL, TAG_COVERED_CELL):
                continue
            repeat = _get_repeat(cell, ATTR_COLS_REPEATED)
            has_value = cell.get(ATTR_VALUE_TYPE) is not None
            for _ in range(repeat):
                cursor += 1
                yield cursor, has_value

    def set_cell(self, sheet_name, row, column, value=None, style_name=None):
        """Set the value and/or style of a specific cell.

        `row`/`column` are 1-based, matching openpyxl's convention.
        Raises `ValueError` if the target position is covered by a merged
        cell, and `IndexError` if it falls outside the sheet's data.
        """
        table = self._table(sheet_name)
        row_el = _locate_indexed(
            table, {TAG_ROW}, TAG_ROW, ATTR_ROWS_REPEATED, row
        )
        cell_el = _locate_indexed(
            row_el, {TAG_CELL, TAG_COVERED_CELL}, TAG_CELL,
            ATTR_COLS_REPEATED, column
        )

        if style_name is not None:
            cell_el.set(ATTR_STYLE_NAME, style_name)

        if value is not None:
            for p in cell_el.findall(TAG_P):
                cell_el.remove(p)
            cell_el.set(ATTR_VALUE_TYPE, 'string')
            p = etree.SubElement(cell_el, TAG_P)
            p.text = str(value)

        return cell_el

    def save(self, path=None):
        """Write the edited document back out as a valid ODS file."""
        target = path or self._path
        new_content = etree.tostring(
            self._root, xml_declaration=True, encoding='UTF-8',
            standalone=True
        )
        tmp_path = target + '.tmp'
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as dst:
            for filename, (info, data) in self._files.items():
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
        self._tables.clear()
        self._registered_styles.clear()