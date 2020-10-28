from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from adminsortable.models import Sortable
from gwml2.models.term import _Term


class Organisation(_Term):
    """ Organisation
    """
    viewers = ArrayField(models.IntegerField(), default=list, null=True)
    editors = ArrayField(models.IntegerField(), default=list, null=True)

    class Meta(Sortable.Meta):
        db_table = 'organisation'
