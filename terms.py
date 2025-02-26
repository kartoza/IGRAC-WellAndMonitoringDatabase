class SheetName:
    """Sheet name of data."""
    general_information = 'General Information'
    hydrogeology = 'Hydrogeology'
    management = 'Management'

    drilling_and_construction = 'Drilling'
    water_strike = 'Water Strike'
    stratigraphic_log = 'Stratigraphic Log'
    structure = 'Construction'

    groundwater_level = 'Groundwater Level'
    groundwater_quality = 'Groundwater Quality'
    abstraction_discharge = 'Abstraction-Discharge'

    def get_uploader(self, sheet_name):
        """Get uploader instance."""
        from gwml2.tasks.uploader import (
            GeneralInformationUploader,
            HydrogeologyUploader,
            ManagementUploader,
            DrillingAndConstructionUploader,
            WaterStrikeUploader,
            StratigraphicLogUploader,
            StructuresUploader,
            MonitoringDataUploader
        )
        # wells.ods
        if sheet_name == self.general_information:
            return GeneralInformationUploader
        elif sheet_name == self.hydrogeology:
            return HydrogeologyUploader
        elif sheet_name == self.management:
            return ManagementUploader

        # drilling_and_construction.ods
        elif sheet_name == self.drilling_and_construction:
            return DrillingAndConstructionUploader
        elif sheet_name == self.water_strike:
            return WaterStrikeUploader
        elif sheet_name == self.stratigraphic_log:
            return StratigraphicLogUploader
        elif sheet_name == self.structure:
            return StructuresUploader

        # monitor_data.ods
        elif sheet_name == self.groundwater_level:
            return MonitoringDataUploader
        elif sheet_name == self.groundwater_quality:
            return MonitoringDataUploader
        elif sheet_name == self.abstraction_discharge:
            return MonitoringDataUploader
        return None

    def get_column_size(self, sheet_name):
        """Get column size."""
        return len(self.get_uploader(sheet_name).RECORD_FORMAT.keys())
