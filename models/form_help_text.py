from django.contrib.gis.db import models


class FormHelpText(models.Model):
    """ Form Help Text """
    form = models.CharField(
        max_length=256)
    field = models.CharField(
        max_length=256)
    help_text = models.CharField(
        null=True, blank=True,
        max_length=256)

    class Meta:
        db_table = 'form_help_text'
        unique_together = ('form', 'field')
