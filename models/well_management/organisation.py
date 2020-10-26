from gwml2.models.term import _Term
from adminsortable.models import Sortable


class Organisation(_Term):
    """ Organisation
    """

    class Meta(Sortable.Meta):
        db_table = 'organisation'
