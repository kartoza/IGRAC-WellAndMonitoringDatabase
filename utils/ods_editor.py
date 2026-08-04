"""Streaming, low-memory editor for existing ODS spreadsheets.

Edits specific (sheet, row, column) cells of an ODS file that already
contains data -- setting a value and/or a style -- without converting
through xlsx and back via an external `soffice` process, and without ever
holding the whole `content.xml` document in memory at once.

Edits are queued with `set_cell()` (cheap, just bookkeeping) and applied in
a single forward streaming pass over `content.xml` inside `save()`: rows are
read, edited if needed, written out and discarded one at a time, so peak
memory stays proportional to a single row rather than the whole document.

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


TAG_DOCUMENT_CONTENT = _q(NS_OFFICE, 'document-content')
TAG_AUTOMATIC_STYLES = _q(NS_OFFICE, 'automatic-styles')
TAG_BODY = _q(NS_OFFICE, 'body')
TAG_SPREADSHEET = _q(NS_OFFICE, 'spreadsheet')
TAG_TABLE = _q(NS_TABLE, 'table')
TAG_ROW = _q(NS_TABLE, 'table-row')
TAG_CELL = _q(NS_TABLE, 'table-cell')
TAG_COVERED_CELL = _q(NS_TABLE, 'covered-table-cell')
TAG_P = _q(NS_TEXT, 'p')
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

# Direct children of these tags that aren't table rows (styles handled
# separately) are opaque, bounded-size content -- pass them through
# untouched instead of trying to understand them.
STRUCTURAL_TAGS = {TAG_DOCUMENT_CONTENT, TAG_BODY, TAG_SPREADSHEET, TAG_TABLE}


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
    """Streaming editor for existing ODS spreadsheets.

    `set_cell()` only queues an edit. The actual read/edit/write happens in
    one forward pass over `content.xml` during `save()`, row by row, so the
    full document is never resident in memory at once.
    """

    def __init__(self, path):
        self._path = path
        self._registered_styles = set()
        self._pending_styles = []
        # resolved sheet name -> {row: [(column, value, style_name), ...]}
        self._edits = {}
        self._sheet_names = []
        # resolved sheet name -> [(1-based column index, has_value), ...]
        self._headers = {}
        self._scan()

    def _scan(self):
        """One low-memory pass to learn sheet names and header columns."""
        with zipfile.ZipFile(self._path) as z, z.open('content.xml') as f:
            context = etree.iterparse(
                f, events=('start', 'end'), huge_tree=True, recover=True
            )
            current_sheet = None
            seen_header = set()
            for event, elem in context:
                if event == 'start' and elem.tag == TAG_TABLE:
                    current_sheet = elem.get(ATTR_TABLE_NAME)
                    self._sheet_names.append(current_sheet)
                elif event == 'end' and elem.tag == TAG_ROW:
                    if current_sheet not in seen_header:
                        seen_header.add(current_sheet)
                        self._headers[current_sheet] = list(
                            self._row_header_columns(elem)
                        )
                    elem.clear()
                elif event == 'end' and elem.tag == TAG_TABLE:
                    elem.clear()

    @staticmethod
    def _row_header_columns(row_el):
        cursor = 0
        for cell in row_el:
            if cell.tag not in (TAG_CELL, TAG_COVERED_CELL):
                continue
            repeat = _get_repeat(cell, ATTR_COLS_REPEATED)
            has_value = cell.get(ATTR_VALUE_TYPE) is not None
            for _ in range(repeat):
                cursor += 1
                yield cursor, has_value

    def sheet_names(self):
        """Return the sheet (table) names in this document."""
        return list(self._sheet_names)

    def _resolve_sheet(self, sheet_name):
        if sheet_name in self._headers:
            return sheet_name
        for name in self._sheet_names:
            if is_correct_sheet(name, sheet_name):
                return name
        raise KeyError(f'Sheet "{sheet_name}" not found')

    def register_style(self, style: OdsCellStyle):
        """Register a cell style so it can be referenced by name."""
        if style.name in self._registered_styles:
            return
        self._pending_styles.append(style)
        self._registered_styles.add(style.name)

    def header_columns(self, sheet_name):
        """Yield (1-based column index, has_value) for row 1 of a sheet."""
        resolved = self._resolve_sheet(sheet_name)
        yield from self._headers.get(resolved, [])

    def set_cell(self, sheet_name, row, column, value=None, style_name=None):
        """Queue a cell edit, applied in one streaming pass by `save()`.

        `row`/`column` are 1-based, matching openpyxl's convention.
        """
        resolved = self._resolve_sheet(sheet_name)
        self._edits.setdefault(resolved, {}).setdefault(row, []).append(
            (column, value, style_name)
        )

    def save(self, path=None):
        """Write the edited document back out as a valid ODS file.

        Streams `content.xml` row by row instead of rewriting a
        fully-parsed DOM, so memory use stays flat regardless of sheet
        size.
        """
        target = path or self._path
        tmp_path = target + '.tmp'
        with zipfile.ZipFile(self._path) as src:
            with zipfile.ZipFile(
                    tmp_path, 'w', zipfile.ZIP_DEFLATED
            ) as dst:
                for info in src.infolist():
                    if info.filename == 'mimetype':
                        dst.writestr(
                            zipfile.ZipInfo('mimetype'),
                            src.read('mimetype'),
                            compress_type=zipfile.ZIP_STORED
                        )
                    elif info.filename == 'content.xml':
                        with src.open('content.xml') as fin:
                            with dst.open(info, 'w') as fout:
                                self._transform(fin, fout)
                    else:
                        with src.open(info.filename) as fin:
                            dst.writestr(info, fin.read())
        os.replace(tmp_path, target)

    def _transform(self, fin, fout):
        """Stream `content.xml` from `fin` to `fout`, applying queued edits
        and injecting styles as rows and tables pass through."""
        context = etree.iterparse(
            fin, events=('start', 'end'), huge_tree=True, recover=True
        )
        open_contexts = []
        current_sheet = None
        cursor = 0

        with etree.xmlfile(fout, encoding='UTF-8') as xf:
            xf.write_declaration(standalone=True)
            for event, elem in context:
                tag = elem.tag

                if event == 'start':
                    if tag == TAG_DOCUMENT_CONTENT:
                        cm = xf.element(
                            tag, dict(elem.attrib), nsmap=elem.nsmap
                        )
                        cm.__enter__()
                        open_contexts.append(cm)
                    elif tag in (TAG_BODY, TAG_SPREADSHEET, TAG_TABLE):
                        cm = xf.element(tag, dict(elem.attrib))
                        cm.__enter__()
                        open_contexts.append(cm)
                        if tag == TAG_TABLE:
                            current_sheet = elem.get(ATTR_TABLE_NAME)
                            cursor = 0
                    continue

                # event == 'end'
                if tag == TAG_ROW:
                    self._write_row(xf, elem, current_sheet, cursor)
                    cursor += _get_repeat(elem, ATTR_ROWS_REPEATED)
                    self._detach(elem)
                    continue

                if tag == TAG_TABLE:
                    open_contexts.pop().__exit__(None, None, None)
                    self._detach(elem)
                    continue

                if tag in (TAG_DOCUMENT_CONTENT, TAG_BODY, TAG_SPREADSHEET):
                    open_contexts.pop().__exit__(None, None, None)
                    self._detach(elem)
                    continue

                if tag == TAG_AUTOMATIC_STYLES:
                    self._inject_styles(elem)
                    xf.write(elem)
                    self._detach(elem)
                    continue

                parent = elem.getparent()
                if parent is not None and parent.tag in STRUCTURAL_TAGS:
                    # Opaque, bounded-size content (table columns,
                    # calculation-settings, scripts, font declarations,
                    # named expressions, ...): pass through untouched.
                    xf.write(elem)
                    self._detach(elem)

    @staticmethod
    def _detach(elem):
        elem.clear()
        parent = elem.getparent()
        if parent is not None:
            while elem.getprevious() is not None:
                del parent[0]

    def _inject_styles(self, styles_elem):
        for style in self._pending_styles:
            styles_elem.append(style.build_element())
        self._pending_styles = []

    def _write_row(self, xf, row_el, sheet_name, cursor):
        repeat = _get_repeat(row_el, ATTR_ROWS_REPEATED)
        edits = self._edits.get(sheet_name)
        if not edits:
            xf.write(row_el)
            return

        if repeat == 1:
            # O(1) lookup -- do NOT scan `edits` here. `edits` can hold
            # tens/hundreds of thousands of rows for a large upload, and
            # this branch runs once per row *element* in the sheet (the
            # common case for real, non-compressed data rows), so a scan
            # here is O(rows x edits) and hangs on large files.
            row_edits = edits.get(cursor + 1)
            if row_edits is None:
                xf.write(row_el)
                return
            self._apply_row_edits(row_el, row_edits)
            xf.write(row_el)
            return

        # repeat > 1 only happens for compressed blocks (usually just the
        # handful of trailing-empty-row blocks per sheet), so scanning
        # `edits` here is cheap -- this is not the hot path.
        targets = sorted(
            r for r in edits if cursor < r <= cursor + repeat
        )
        if not targets:
            xf.write(row_el)
            return

        # Split the repeated block so each targeted logical row becomes
        # its own element, and the untouched runs around it stay
        # compressed.
        start, end = cursor + 1, cursor + repeat
        cur = start
        for target in targets:
            gap = target - cur
            if gap > 0:
                gap_el = copy.deepcopy(row_el)
                _set_repeat(gap_el, ATTR_ROWS_REPEATED, gap)
                xf.write(gap_el)
            target_el = copy.deepcopy(row_el)
            _set_repeat(target_el, ATTR_ROWS_REPEATED, 1)
            self._apply_row_edits(target_el, edits[target])
            xf.write(target_el)
            cur = target + 1
        if cur <= end:
            tail_el = copy.deepcopy(row_el)
            _set_repeat(tail_el, ATTR_ROWS_REPEATED, end - cur + 1)
            xf.write(tail_el)

    @staticmethod
    def _apply_row_edits(row_el, cell_edits):
        for column, value, style_name in cell_edits:
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

    def close(self):
        self._edits.clear()
        self._headers.clear()
        self._registered_styles.clear()