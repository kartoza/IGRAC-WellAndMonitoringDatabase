"""Check template data."""
import zipfile

from lxml import etree

from gwml2.utils.template_check import START_ROW

namespace = {
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
}


def is_correct_sheet(current_sheet, sheet_name):
    """Is this correct sheet."""
    return current_sheet in [
        sheet_name.replace(' ', '_'),
        sheet_name.replace('_', ' ')
    ]


def get_count(file_path: str, sheet_name: str) -> int:
    """Get data from records."""

    if not file_path:
        raise Exception('file_path cannot be empty')

    with zipfile.ZipFile(file_path, "r") as zf:
        with zf.open("content.xml") as xml_file:
            context = etree.iterparse(
                xml_file, events=("start", "end"), huge_tree=True,
                recover=True
            )

            count = None
            current_sheet = None
            for event, elem in context:
                if event == "start" and elem.tag.endswith("table"):
                    current_sheet = elem.attrib.get(
                        '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name',
                        'Unknown Sheet'
                    )
                    if is_correct_sheet(current_sheet, sheet_name):
                        count = 0

                if event == "end" and elem.tag.endswith("table-row"):
                    # Extract cell values
                    cell_values = [
                        "".join(cell.xpath('.//text:p/text()', namespaces={
                            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                        })).strip()
                        for cell in
                        elem.xpath('.//table:table-cell', namespaces=namespace)
                    ]

                    # Check if row is empty (all cells are blank)
                    if any(cell_values) and is_correct_sheet(
                            current_sheet, sheet_name
                    ):
                        count += 1

                    # Free memory
                    elem.clear()

            # Return count if none
            if count is None:
                return None
            return count - START_ROW


def extract_data(file_path: str, sheet_name: str, receiver):
    """Extract data from filepath."""

    with zipfile.ZipFile(file_path, "r") as zf:
        with zf.open("content.xml") as xml_file:
            context = etree.iterparse(
                xml_file, events=("start", "end"), huge_tree=True,
                recover=True
            )
            namespace = {
                'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}

            current_sheet = None
            for event, elem in context:
                if event == "start" and elem.tag.endswith("table"):
                    current_sheet = elem.attrib.get(
                        '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name',
                        'Unknown Sheet'
                    )

                if event == "end" and elem.tag.endswith("table-row"):
                    # continue if not correct sheet
                    if not is_correct_sheet(current_sheet, sheet_name):
                        continue

                    # Get row data
                    row_data = []
                    for cell in elem.xpath(
                            './/table:table-cell', namespaces=namespace
                    ):
                        spanned = int(
                            cell.attrib.get(
                                '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-spanned',
                                '1'
                            )
                        )
                        repeated = int(
                            cell.attrib.get(
                                '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated',
                                '1'
                            )
                        )

                        # Extract cell value
                        cell_value = cell.xpath(
                            './/text:p/text()',
                            namespaces={
                                'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                            }
                        )
                        if not cell_value:
                            value_type = cell.attrib.get(
                                'office:value-type')
                            if value_type == 'float':
                                cell_value = [
                                    cell.attrib.get('office:value')
                                ]
                            elif value_type == 'date':
                                cell_value = [
                                    cell.attrib.get('office:date-value')
                                ]

                        cell_content = ' '.join(
                            cell_value
                        ) if cell_value else ''

                        # Create empty data
                        for repeat in range(repeated):
                            for _ in range(spanned):
                                if _ == 0:
                                    row_data.append(cell_content)
                                else:
                                    row_data.append('')

                    if row_data[0]:
                        receiver(row_data)

                    # Free memory
                    elem.clear()
