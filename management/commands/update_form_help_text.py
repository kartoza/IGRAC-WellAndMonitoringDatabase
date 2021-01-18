from django.core.management.base import BaseCommand
from gwml2.forms.well.construction import ConstructionForm
from gwml2.forms.well.construction_structure import ConstructionStructureForm
from gwml2.forms.well.document import DocumentForm
from gwml2.forms.well.drilling import DrillingForm
from gwml2.forms.well.general_information import GeneralInformationForm
from gwml2.forms.well.geology import GeologyForm
from gwml2.forms.well.hydrogeology import HydrogeologyParameterForm
from gwml2.forms.well.license import LicenseForm
from gwml2.forms.well.management import ManagementForm
from gwml2.forms.well.pumping_test import PumpingTestForm
from gwml2.forms.well.stratigraphic_log import StratigraphicLogForm
from gwml2.forms.well.water_strike import WaterStrikeForm
from gwml2.forms.well.well_metadata import WellMetadataForm
from gwml2.forms.well.measurement.level_measurement import WellLevelMeasurementForm
from gwml2.forms.well.measurement.quality_measurement import WellQualityMeasurementForm
from gwml2.forms.well.measurement.yield_measurement import WellYieldMeasurementForm
from gwml2.models.form_help_text import FormHelpText


class Command(BaseCommand):
    """ Update all fixtures
    """
    args = ''
    help = 'Reupdate all form help text.'

    def handle(self, *args, **options):
        forms = [
            ConstructionForm(),
            ConstructionStructureForm(),
            DocumentForm(),
            DrillingForm(),
            GeneralInformationForm(),
            GeologyForm(),
            HydrogeologyParameterForm(),
            LicenseForm(),
            ManagementForm(),
            PumpingTestForm(),
            StratigraphicLogForm(),
            WaterStrikeForm(),
            WellMetadataForm(),
            WellLevelMeasurementForm(),
            WellQualityMeasurementForm(),
            WellYieldMeasurementForm()
        ]
        for form in forms:
            for field_name, field in form.fields.items():
                FormHelpText.objects.get_or_create(
                    form=form.__class__.__name__,
                    field=field_name,
                    defaults={
                        'help_text': field.help_text
                    }
                )
