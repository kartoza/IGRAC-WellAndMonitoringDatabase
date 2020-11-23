from rest_framework import serializers
from gwml2.models.well import Well
from gwml2.serializer.general import WellSerializer
from gwml2.serializer.well.construction import ConstructionSerializer
from gwml2.serializer.well.drilling import DrillingSerializer
from gwml2.serializer.well.geology import GeologySerializer
from gwml2.serializer.well.hydrogeology import HydrogeologyParameterSerializer
from gwml2.serializer.well.management import ManagementSerializer
from gwml2.serializer.well.measurement import (
    WellLevelMeasurementSerializer, WellQualityMeasurementSerializer, WellYieldMeasurementSerializer)
from gwml2.models.general import Quantity


class GeneralInformationSerializer(WellSerializer, serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        """ Return latitude of well
        :param obj:
        :type obj: Well
        """
        if obj.location:
            return round(obj.location.y, 7)
        else:
            return None

    def get_longitude(self, obj):
        """ Return longitude of well
        :param obj:
        :type obj: Well
        """
        if obj.location:
            return round(obj.location.x, 7)
        else:
            return None

    class Meta:
        model = Well
        fields = [
            'original_id', 'organisation', 'name', 'status', 'feature_type',
            'purpose', 'description', 'latitude', 'longitude', 'country', 'address']

    def to_representation(self, instance):
        """ Custom representation on the result
        :param instance:
        :type instance: Well
        """
        result = super(GeneralInformationSerializer, self).to_representation(instance)
        result.update(self.quantity('ground_surface_elevation', instance.ground_surface_elevation))
        result.update(self.quantity('top_borehole_elevation', instance.top_borehole_elevation))
        return result


class WellLikeFormSerializer(WellSerializer, serializers.ModelSerializer):
    general_information = serializers.SerializerMethodField()
    geology = serializers.SerializerMethodField()
    drilling = serializers.SerializerMethodField()
    construction = serializers.SerializerMethodField()
    hydrogeology = serializers.SerializerMethodField()
    management = serializers.SerializerMethodField()

    level_measurement = serializers.SerializerMethodField()
    quality_measurement = serializers.SerializerMethodField()
    yield_measurement = serializers.SerializerMethodField()

    def get_general_information(self, obj):
        """ Return general information of well
        :param obj:
        :type obj: Well
        """
        return GeneralInformationSerializer(obj).data

    def get_geology(self, obj):
        """ Return geology of well
        :param obj:
        :type obj: Well
        """
        return GeologySerializer(obj.geology).data

    def get_drilling(self, obj):
        """ Return drilling of well
        :param obj:
        :type obj: Well
        """
        return DrillingSerializer(obj.drilling).data

    def get_construction(self, obj):
        """ Return construction of well
        :param obj:
        :type obj: Well
        """
        return ConstructionSerializer(obj.construction).data

    def get_hydrogeology(self, obj):
        """ Return hydrogeology of well
        :param obj:
        :type obj: Well
        """
        return HydrogeologyParameterSerializer(obj.hydrogeology_parameter).data

    def get_management(self, obj):
        """ Return management of well
        :param obj:
        :type obj: Well
        """
        return ManagementSerializer(obj.management).data

    def get_level_measurement(self, obj):
        """ Return level_measurement of well
        :param obj:
        :type obj: Well
        """
        return WellLevelMeasurementSerializer(
            obj.welllevelmeasurement_set.all(), many=True).data

    def get_quality_measurement(self, obj):
        """ Return quality_measurement of well
        :param obj:
        :type obj: Well
        """
        return WellQualityMeasurementSerializer(
            obj.wellqualitymeasurement_set.all(), many=True).data

    def get_yield_measurement(self, obj):
        """ Return yield_measurement of well
        :param obj:
        :type obj: Well
        """
        return WellYieldMeasurementSerializer(
            obj.wellyieldmeasurement_set.all(), many=True).data

    class Meta:
        model = Well
        fields = [
            'general_information', 'geology', 'drilling', 'construction',
            'hydrogeology', 'management',
            'level_measurement', 'quality_measurement', 'yield_measurement'
        ]


class WellMinimizedSerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = Well
        fields = []

    def get_val(self, value):
        if value is None:
            return ''
        else:
            if value is False:
                return 'f'
            elif value is True:
                return 't'
        return value if value else ''

    def term_val(self, value):
        """ return value of term """
        return value.name if value else ''

    def get_quantity(self, value):
        """ return value of quantity """
        return value.__str__() if value else ''

    def get_length_to_meter(self, value):
        """ return value of quantity of lenght to meter
        :type value: Quantity
        """
        if not value:
            return ''
        else:
            return value.convert('m')

    def to_representation(self, instance):
        """ Custom representation on the result
        :type instance: Well
        """
        result = super(WellMinimizedSerializer, self).to_representation(instance)
        result['id'] = instance.original_id  # Original ID
        result['loc'] = [  # location
            round(instance.location.y, 7), round(instance.location.x, 7)
        ]
        result['dt'] = int(instance.last_edited_at.timestamp())  # Time updated
        result['org'] = self.term_val(instance.organisation)  # Organisation
        result['st'] = self.term_val(instance.status)  # Status
        result['ft'] = self.term_val(instance.feature_type)  # Feature type
        result['p'] = self.term_val(instance.purpose)  # Purpose
        result['dsc'] = self.get_val(instance.description)  # description
        result['gse'] = self.get_length_to_meter(  # Ground_surface_elevation
            instance.ground_surface_elevation)
        result['tbe'] = self.get_length_to_meter(  # Top_borehole_elevation
            instance.top_borehole_elevation)
        result['c'] = self.term_val(instance.country)  # Country
        result['adr'] = self.get_val(instance.address)  # Address

        # Drilling
        result['dtd'] = self.get_length_to_meter(  # Total depth
            instance.geology.total_depth) if instance.geology else ''
        result['ddm'] = self.term_val(  # Drilling : Drilling method
            instance.drilling.drilling_method) if instance.drilling else ''
        result['dd'] = self.get_val(  # Drilling : driller
            instance.drilling.driller) if instance.drilling else ''
        result['ds'] = self.get_val(  # Drilling : successful
            instance.drilling.successful) if instance.drilling else ''
        result['dr'] = self.get_val(  # Drilling : cause_of_failure
            instance.drilling.cause_of_failure) if instance.drilling else ''
        result['dy'] = self.get_val(  # Drilling : year_of_drilling
            instance.drilling.year_of_drilling) if instance.drilling else ''

        # Water Strike
        result['ws'] = []
        if instance.drilling:
            for water_strike in instance.drilling.waterstrike_set.all():
                result['ws'].append({
                    'id': water_strike.id,  # id
                    'ref': self.term_val(  # reference
                        water_strike.depth.reference) if water_strike.depth else '',
                    'd': self.get_length_to_meter(  # depth
                        water_strike.depth.value) if water_strike.depth else '',
                    'dsc': self.get_val(water_strike.description)  # description
                })
        # Stratigraphic Log
        result['sl'] = []
        if instance.drilling:
            for log in instance.drilling.stratigraphiclog_set.all():
                result['sl'].append({
                    'id': log.id,  # id
                    'ref': self.term_val(  # reference
                        log.reference_elevation),
                    'td': self.get_length_to_meter(  # top depth
                        log.top_depth),
                    'bd': self.get_length_to_meter(  # bottom depth
                        log.bottom_depth),
                    'm': self.get_val(  # Material
                        log.material),
                    'u': self.get_val(  # Unit
                        log.stratigraphic_unit),
                })

        # Construction
        result['cpi'] = self.get_val(  # Construction : Pump installer
            instance.construction.pump_installer) if instance.construction else ''
        result['cpd'] = self.get_val(  # Construction : Pump description
            instance.construction.pump_description) if instance.construction else ''

        # Construction Structures
        result['cs'] = []
        if instance.construction:
            for log in instance.construction.constructionstructure_set.all():
                result['cs'].append({
                    'id': log.id,  # id
                    'typ': self.term_val(  # type
                        log.type),
                    'ref': self.term_val(  # reference
                        log.reference_elevation),
                    'td': self.get_length_to_meter(  # top depth
                        log.top_depth),
                    'bd': self.get_length_to_meter(  # bottom depth
                        log.bottom_depth),
                    'dia': self.get_length_to_meter(  # diameter
                        log.diameter),
                    'm': self.get_val(  # Material
                        log.material),
                    'dsc': self.get_val(  # Unit
                        log.description),
                })

        # Hydrogeology
        result['an'] = self.get_val(  # Hydrogeology : Aquifer name
            instance.hydrogeology_parameter.aquifer_name) if instance.hydrogeology_parameter else ''
        result['am'] = self.get_val(  # Hydrogeology : Aquifer material
            instance.hydrogeology_parameter.aquifer_material) if instance.hydrogeology_parameter else ''
        result['at'] = self.term_val(  # Hydrogeology : Aquifer type
            instance.hydrogeology_parameter.aquifer_type) if instance.hydrogeology_parameter else ''
        result['atn'] = self.get_length_to_meter(  # Hydrogeology : Aquifer thickness
            instance.hydrogeology_parameter.aquifer_thickness) if instance.hydrogeology_parameter else ''
        result['ac'] = self.term_val(  # Hydrogeology : Confinement
            instance.hydrogeology_parameter.confinement) if instance.hydrogeology_parameter else ''
        result['adc'] = self.get_val(  # Hydrogeology : Degree of Confinement
            instance.hydrogeology_parameter.degree_of_confinement) if instance.hydrogeology_parameter else ''

        # Hydraulic properties
        result['hp'] = self.get_val(  # Hydraulic properties : Porosity
            instance.hydrogeology_parameter.pumping_test.porosity) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''
        result['hc'] = self.get_length_to_meter(  # Hydraulic properties : Hydraulic conductivity
            instance.hydrogeology_parameter.pumping_test.hydraulic_conductivity) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''
        result['ht'] = self.get_length_to_meter(  # Hydraulic properties : Transmissivity
            instance.hydrogeology_parameter.pumping_test.transmissivity) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''
        result['hss'] = self.get_length_to_meter(  # Hydraulic properties : Specific storage
            instance.hydrogeology_parameter.pumping_test.specific_storage) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''
        result['hsc'] = self.get_length_to_meter(  # Hydraulic properties : Specific capacity
            instance.hydrogeology_parameter.pumping_test.specific_capacity) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''
        result['hs'] = self.get_val(  # Hydraulic properties : Storativity
            instance.hydrogeology_parameter.pumping_test.storativity) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''
        result['htt'] = self.get_val(  # Hydraulic properties : Test Type
            instance.hydrogeology_parameter.pumping_test.test_type) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''

        # Management
        result['mm'] = self.get_val(  # Management : Manager
            instance.management.manager) \
            if instance.management else ''
        result['md'] = self.get_val(  # Management : Description
            instance.management.description) \
            if instance.management else ''
        result['mgu'] = self.term_val(  # Management : Groundwater use
            instance.management.groundwater_use) \
            if instance.management else ''
        result['mn'] = self.get_val(  # Management : Number of people served
            instance.management.number_of_users) \
            if instance.management else ''

        # License
        result['mln'] = self.get_val(  # License : Number
            instance.management.license.number) \
            if instance.management and instance.management.license else ''
        result['mlf'] = self.get_val(  # License : Valid From
            instance.management.license.valid_from) \
            if instance.management and instance.management.license else ''
        result['mlu'] = self.get_val(  # License : Valid Until
            instance.management.license.valid_until) \
            if instance.management and instance.management.license else ''
        result['mld'] = self.get_val(  # License : Valid Description
            instance.management.license.description) \
            if instance.management and instance.management.license else ''

        # Level Measurement
        result['lm'] = []
        for measurement in instance.welllevelmeasurement_set.all():
            result['lm'].append({
                'id': measurement.id,
                'dt': measurement.time.timestamp(),
                'par': self.term_val(measurement.parameter),
                'mt': self.get_val(measurement.methodology),
                'v': self.get_length_to_meter(measurement.value),
            })

        # Quality Measurement
        result['qm'] = []
        for measurement in instance.wellqualitymeasurement_set.all():
            result['qm'].append({
                'id': measurement.id,
                'dt': measurement.time.timestamp(),
                'par': self.term_val(measurement.parameter),
                'mt': self.get_val(measurement.methodology),
                'v': self.get_length_to_meter(measurement.value),
            })

        # Yield Measurement
        result['ym'] = []
        for measurement in instance.wellyieldmeasurement_set.all():
            result['ym'].append({
                'id': measurement.id,
                'dt': measurement.time.timestamp(),
                'par': self.term_val(measurement.parameter),
                'mt': self.get_val(measurement.methodology),
                'v': self.get_length_to_meter(measurement.value),
            })
        return result
