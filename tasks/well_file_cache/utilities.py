import os

from gwml2.models.term import TermFeatureType


def zipdir(path, ziph):
    """Zip directory"""
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(
                    os.path.join(root, file), os.path.join(path, '..')
                )
            )


def get_data(id, cache, Term):
    """Get data that on cache or not."""
    if not id:
        return ''
    if id not in cache:
        try:
            value = Term.objects.get(id=id).__str__()
        except TermFeatureType.DoesNotExist:
            value = ''
        cache[id] = value
        return value
    return cache[id]