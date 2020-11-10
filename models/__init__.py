from gwml2.models.construction import *
from gwml2.models.download_session import *
from gwml2.models.drilling import *
from gwml2.models.general import *
from gwml2.models.general_information import *
from gwml2.models.geology import *
from gwml2.models.hydrogeology import *
from gwml2.models.management import *
from gwml2.models.measurement import *
from gwml2.models.term import *
from gwml2.models.term_measurement_parameter import *
from gwml2.models.well import *

# management
from gwml2.models.well_management.organisation import *
from gwml2.models.well_management.user import *

# for signals models
from gwml2.signals import *


@receiver(post_save)
def data_deleted(sender, instance, **kwargs):
    if sender._meta.app_label == 'gwml2' and sender._meta.object_name != 'DownloadSession':
        DownloadSession.objects.all().delete()
