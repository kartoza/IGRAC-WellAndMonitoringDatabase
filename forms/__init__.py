from gwml2.forms.uploader.csv_well_form import CsvWellForm
from gwml2.forms.well.construction import ConstructionForm
from gwml2.forms.well.construction_structure import ConstructionStructureForm
from gwml2.forms.well.document import DocumentForm
from gwml2.forms.well.drilling import DrillingForm
from gwml2.forms.well.general_information import GeneralInformationForm
from gwml2.forms.well.geology import GeologyForm
from gwml2.forms.well.stratigraphic_log import StratigraphicLogForm
from gwml2.forms.well.hydrogeology import HydrogeologyParameterForm
from gwml2.forms.well.pumping_test import PumpingTestForm
from gwml2.forms.well.license import LicenseForm
from gwml2.forms.well.management import ManagementForm
from gwml2.forms.well.measurement.level_measurement import WellLevelMeasurementForm
from gwml2.forms.well.measurement.quality_measurement import WellQualityMeasurementForm
from gwml2.forms.well.measurement.yield_measurement import WellYieldMeasurementForm
from gwml2.forms.well.reference_elevation import ReferenceElevationForm
from gwml2.forms.well.water_strike import WaterStrikeForm
from gwml2.forms.well.well_metadata import WellMetadataForm


def get_form_from_model(relation_model_name):
    """ Return form from model """
    if relation_model_name == 'WellDocument':
        return DocumentForm
    elif relation_model_name == 'WaterStrike':
        return WaterStrikeForm
    elif relation_model_name == 'StratigraphicLog':
        return StratigraphicLogForm
    elif relation_model_name == 'ConstructionStructure':
        return ConstructionStructureForm
    elif relation_model_name == 'WellLevelMeasurement':
        return WellLevelMeasurementForm
    elif relation_model_name == 'WellQualityMeasurement':
        return WellQualityMeasurementForm
    elif relation_model_name == 'WellYieldMeasurement':
        return WellYieldMeasurementForm
    return None
