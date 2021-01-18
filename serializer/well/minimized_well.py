from rest_framework import serializers
from gwml2.models.well import Well, WellLevelMeasurement
from gwml2.serializer.general import WellSerializer


class WellMeasurementMinimizedSerializer(WellSerializer, serializers.ModelSerializer):
    dt = serializers.SerializerMethodField()
    par = serializers.SerializerMethodField()
    mt = serializers.SerializerMethodField()
    v = serializers.SerializerMethodField()
    u = serializers.SerializerMethodField()

    class Meta:
        model = WellLevelMeasurement
        fields = ['id', 'dt', 'par', 'mt', 'v', 'u']

    def get_dt(self, obj):
        return obj.time.timestamp()

    def get_par(self, obj):
        return self.term_val(obj.parameter)

    def get_mt(self, obj):
        return self.get_val(obj.methodology)

    def get_v(self, obj):
        return self.get_length_to_meter(obj.value)

    def get_u(self, obj):
        return self.get_val(obj.value.unit.name) if obj.value and obj.value.unit else ''


class WellMinimizedSerializer(WellSerializer, serializers.ModelSerializer):
    class Meta:
        model = Well
        fields = []

    def to_representation(self, instance):
        """ Custom representation on the result
        :type instance: Well
        """
        result = super(WellMinimizedSerializer, self).to_representation(instance)
        result['pk'] = instance.id  # ID
        result['id'] = instance.original_id  # Original ID
        result['nm'] = instance.name  # Well name
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
                        water_strike.reference_elevation) if water_strike.reference_elevation else '',
                    'd': self.get_length_to_meter(  # depth
                        water_strike.depth) if water_strike.depth else '',
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
        result['atn'] = instance.hydrogeology_parameter.aquifer_thickness if instance.hydrogeology_parameter else ''
        result['ac'] = self.term_val(  # Hydrogeology : Confinement
            instance.hydrogeology_parameter.confinement) if instance.hydrogeology_parameter else ''
        result['adc'] = self.get_val(  # Hydrogeology : Degree of Confinement
            instance.hydrogeology_parameter.degree_of_confinement) if instance.hydrogeology_parameter else ''

        # Hydraulic properties
        result['hp'] = self.get_val(
            instance.hydrogeology_parameter.pumping_test.porosity) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Porosity
        result['hc'] = instance.hydrogeology_parameter.pumping_test.hydraulic_conductivity.__str__() \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Hydraulic conductivity

        result['ht'] = instance.hydrogeology_parameter.pumping_test.transmissivity.__str__() \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Transmissivity
        result['hss'] = instance.hydrogeology_parameter.pumping_test.specific_storage.__str__() \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Specific storage
        result['hsc'] = instance.hydrogeology_parameter.pumping_test.specific_capacity.__str__() \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Specific capacity
        result['hs'] = instance.hydrogeology_parameter.pumping_test.storativity.__str__() \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Storativity
        result['htt'] = self.get_val(instance.hydrogeology_parameter.pumping_test.test_type) \
            if instance.hydrogeology_parameter and instance.hydrogeology_parameter.pumping_test else ''  # Hydraulic properties : Test Type

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
        result['lm'] = WellMeasurementMinimizedSerializer(
            instance.welllevelmeasurement_set.all()[:10], many=True).data

        # Quality Measurement
        result['qm'] = WellMeasurementMinimizedSerializer(
            instance.wellqualitymeasurement_set.all()[:10], many=True).data

        # Yield Measurement
        result['ym'] = WellMeasurementMinimizedSerializer(
            instance.wellyieldmeasurement_set.all()[:10], many=True).data
        return result
