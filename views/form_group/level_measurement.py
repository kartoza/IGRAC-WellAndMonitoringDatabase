from gwml2.forms import (
    WellGroundwaterLevelMeasurementForm, ReferenceElevationForm)
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.models.well import WellGroundwaterLevelMeasurement, WellGroundwaterLevel
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class LevelMeasurementGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        measurements = []
        if self.well.groundwater_level:
            for measurement in self.well.groundwater_level.wellgroundwaterlevelmeasurement_set.all():
                measurements.append(WellGroundwaterLevelMeasurementForm.make_from_instance(
                    measurement))
        return {
            'level_measurement_elevation': ReferenceElevationForm.make_from_instance(
                self.well.groundwater_level.reference_elevation if self.well.groundwater_level else None),
            'level_measurement': WellGroundwaterLevelMeasurementForm(),  # manytomany form
            'level_measurements': measurements,  # manytomany data
        }


class LevelMeasurementCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    well_level = None
    measurements = []

    def create(self):
        """ create form from data
        """
        self.measurements = []
        self.well_level = self.well.groundwater_level if self.well.groundwater_level else WellGroundwaterLevel()

        # reference elevation
        self.elevation_form = self._make_form(
            self.well_level.reference_elevation \
                if self.well_level.reference_elevation else ReferenceElevation(),
            ReferenceElevationForm, self.data['level_measurement']['reference_elevation'])

        for measurement in self.data['level_measurement']['measurements']:
            if not measurement['time']:
                return
            obj = WellGroundwaterLevelMeasurement.objects.get(
                id=measurement['id_']) if measurement['id_'] else WellGroundwaterLevelMeasurement()

            self.measurements.append(
                self._make_form(
                    obj, WellGroundwaterLevelMeasurementForm, measurement
                )
            )

    def save(self):
        """ save all available data """
        self.elevation_form.save()
        self.well_level.reference_elevation = self.elevation_form.instance
        self.well_level.save()
        for measurement in self.measurements:
            measurement.instance.groundwater_level = self.well_level
            measurement.save()
        self.well.groundwater_level = self.well_level
