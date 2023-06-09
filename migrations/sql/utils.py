"""Utils for sql."""
import os


def load_sql(folder, filename):
    """Load sql."""
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        folder, filename
    )
    return open(file_path).read()
