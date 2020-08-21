from datetime import datetime
from django.contrib.gis.db import models


class Document(models.Model):
    uploaded_at = models.DateTimeField(
        default=datetime.now, blank=True)
    file = models.FileField(
        null=True, blank=True,
        upload_to='gwml2/document/'
    )
    file_path = models.CharField(
        null=True, blank=True,
        max_length=512
    )
    description = models.TextField(
        null=True, blank=True,
        help_text="Description of the feature."
    )

    class Meta:
        db_table = 'document'
        abstract = True
