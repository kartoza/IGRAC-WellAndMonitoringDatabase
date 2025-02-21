"""Check template data."""
import zipfile

from lxml import etree

from gwml2.utils.template_check import START_ROW

namespace = {
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
}


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
                    if current_sheet in [
                        sheet_name.replace(' ', '_'),
                        sheet_name.replace('_', ' ')
                    ]:
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
                    if any(cell_values):
                        if current_sheet in [
                            sheet_name.replace(' ', '_'),
                            sheet_name.replace('_', ' ')
                        ]:
                            count += 1

                    # Free memory
                    elem.clear()

            # Return count if none
            if count is None:
                return None
            return count - START_ROW
