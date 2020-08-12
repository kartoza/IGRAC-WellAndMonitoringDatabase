create table if not exists gwml2_country
(
	id serial not null
		constraint gwml2_country_pkey
			primary key,
	name varchar(512) not null,
	code varchar(126) not null,
	geometry geometry(MultiPolygon,4326)
);

create index if not exists gwml2_country_geometry_id
	on gwml2_country (geometry);

create table if not exists gwml2_license
(
	id serial not null
		constraint gwml2_license_pkey
			primary key,
	number varchar(512) not null,
	valid_from date not null,
	valid_until date not null,
	description text
);

create table if not exists gwml2_termaquifertype
(
	id serial not null
		constraint gwml2_termaquifertype_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termaquifertype_name_key
			unique,
	description text
);

create index if not exists gwml2_termaquifertype_name_bdaebfbb_like
	on gwml2_termaquifertype (name);

create table if not exists gwml2_termconfinement
(
	id serial not null
		constraint gwml2_termconfinement_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termconfinement_name_key
			unique,
	description text
);

create index if not exists gwml2_termconfinement_name_7f9fd793_like
	on gwml2_termconfinement (name);

create table if not exists gwml2_termdrillingmethod
(
	id serial not null
		constraint gwml2_termdrillingmethod_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termdrillingmethod_name_key
			unique,
	description text
);

create index if not exists gwml2_termdrillingmethod_name_07b88648_like
	on gwml2_termdrillingmethod (name);

create table if not exists gwml2_termfeaturetype
(
	id serial not null
		constraint gwml2_termfeaturetype_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termfeaturetype_name_key
			unique,
	description text
);

create index if not exists gwml2_termfeaturetype_name_ba3e276d_like
	on gwml2_termfeaturetype (name);

create table if not exists gwml2_termgroundwateruse
(
	id serial not null
		constraint gwml2_termgroundwateruse_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termgroundwateruse_name_key
			unique,
	description text
);

create table if not exists gwml2_management
(
	id serial not null
		constraint gwml2_management_pkey
			primary key,
	manager varchar(512) not null,
	description text,
	number_of_users integer,
	groundwater_use_id integer
		constraint gwml2_management_groundwater_use_id_91dfb645_fk_gwml2_ter
			references gwml2_termgroundwateruse
				deferrable initially deferred,
	license_id integer
		constraint gwml2_management_license_id_b49cd675_fk_gwml2_license_id
			references gwml2_license
				deferrable initially deferred
);

create index if not exists gwml2_management_groundwater_use_id_91dfb645
	on gwml2_management (groundwater_use_id);

create index if not exists gwml2_management_license_id_b49cd675
	on gwml2_management (license_id);

create index if not exists gwml2_termgroundwateruse_name_914d9e07_like
	on gwml2_termgroundwateruse (name);

create table if not exists gwml2_termmeasurementparameter
(
	id serial not null
		constraint gwml2_termmeasurementparameter_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termmeasurementparameter_name_key
			unique,
	description text
);

create index if not exists gwml2_termmeasurementparameter_name_0a15889b_like
	on gwml2_termmeasurementparameter (name);

create table if not exists gwml2_termwellpurpose
(
	id serial not null
		constraint gwml2_termwellpurpose_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_termwellpurpose_name_key
			unique,
	description text
);

create index if not exists gwml2_termwellpurpose_name_4d070c0d_like
	on gwml2_termwellpurpose (name);

create table if not exists gwml2_unit
(
	id serial not null
		constraint gwml2_unit_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_unit_name_key
			unique,
	description text
);

create table if not exists gwml2_quantity
(
	id serial not null
		constraint gwml2_quantity_pkey
			primary key,
	value double precision not null,
	unit_id integer
		constraint gwml2_quantity_unit_id_3fcefe49_fk_gwml2_unit_id
			references gwml2_unit
				deferrable initially deferred
);

create index if not exists gwml2_quantity_unit_id_3fcefe49
	on gwml2_quantity (unit_id);

create table if not exists gwml2_referenceelevation
(
	id serial not null
		constraint gwml2_referenceelevation_pkey
			primary key,
	description text,
	value_id integer
		constraint gwml2_referenceelevation_value_id_key
			unique
		constraint gwml2_referenceelevation_value_id_5c91413f_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

create table if not exists gwml2_construction
(
	id serial not null
		constraint gwml2_construction_pkey
			primary key,
	pump_installer varchar(512),
	pump_description text,
	reference_elevation_id integer
		constraint gwml2_construction_reference_elevation_id_key
			unique
		constraint gwml2_construction_reference_elevation__92d2c234_fk_gwml2_ref
			references gwml2_referenceelevation
				deferrable initially deferred
);

create table if not exists gwml2_drilling
(
	id serial not null
		constraint gwml2_drilling_pkey
			primary key,
	driller varchar(512),
	successful boolean,
	failed_explanation text,
	drilling_method_id integer
		constraint gwml2_drilling_drilling_method_id_ba8fe9bf_fk_gwml2_ter
			references gwml2_termdrillingmethod
				deferrable initially deferred,
	reference_elevation_id integer
		constraint gwml2_drilling_reference_elevation_id_key
			unique
		constraint gwml2_drilling_reference_elevation__f01a95f9_fk_gwml2_ref
			references gwml2_referenceelevation
				deferrable initially deferred,
	total_depth_id integer
		constraint gwml2_drilling_total_depth_id_key
			unique
		constraint gwml2_drilling_total_depth_id_d4bc4245_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

create index if not exists gwml2_drilling_drilling_method_id_ba8fe9bf
	on gwml2_drilling (drilling_method_id);

create index if not exists gwml2_unit_name_2201163b_like
	on gwml2_unit (name);

create table if not exists gwml2_wellgroundwaterlevel
(
	id serial not null
		constraint gwml2_wellgroundwaterlevel_pkey
			primary key,
	reference_elevation_id integer
		constraint gwml2_wellgroundwaterlevel_reference_elevation_id_key
			unique
		constraint gwml2_wellgroundwate_reference_elevation__14102ad7_fk_gwml2_ref
			references gwml2_referenceelevation
				deferrable initially deferred
);

create table if not exists gwml2_waterstrike
(
	id serial not null
		constraint gwml2_waterstrike_pkey
			primary key,
	description text,
	depth_id integer
		constraint gwml2_waterstrike_depth_id_key
			unique
		constraint gwml2_waterstrike_depth_id_21df82f1_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	drilling_id integer
		constraint gwml2_waterstrike_drilling_id_adda76dc_fk_gwml2_drilling_id
			references gwml2_drilling
				deferrable initially deferred
);

create index if not exists gwml2_waterstrike_drilling_id_adda76dc
	on gwml2_waterstrike (drilling_id);

create table if not exists gwml2_unitgroup
(
	id serial not null
		constraint gwml2_unitgroup_pkey
			primary key,
	name varchar(512) not null
		constraint gwml2_unitgroup_name_key
			unique,
	description text
);

create index if not exists gwml2_unitgroup_name_90d3a956_like
	on gwml2_unitgroup (name);

create table if not exists gwml2_unitgroup_units
(
	id serial not null
		constraint gwml2_unitgroup_units_pkey
			primary key,
	unitgroup_id integer not null
		constraint gwml2_unitgroup_unit_unitgroup_id_51afd0de_fk_gwml2_uni
			references gwml2_unitgroup
				deferrable initially deferred,
	unit_id integer not null
		constraint gwml2_unitgroup_units_unit_id_d55d9269_fk_gwml2_unit_id
			references gwml2_unit
				deferrable initially deferred,
	constraint gwml2_unitgroup_units_unitgroup_id_unit_id_0bebcffd_uniq
		unique (unitgroup_id, unit_id)
);

create index if not exists gwml2_unitgroup_units_unitgroup_id_51afd0de
	on gwml2_unitgroup_units (unitgroup_id);

create index if not exists gwml2_unitgroup_units_unit_id_d55d9269
	on gwml2_unitgroup_units (unit_id);

create table if not exists gwml2_stratigraphiclog
(
	id serial not null
		constraint gwml2_stratigraphiclog_pkey
			primary key,
	material varchar(512),
	stratigraphic_unit varchar(256),
	bottom_depth_id integer
		constraint gwml2_stratigraphiclog_bottom_depth_id_key
			unique
		constraint gwml2_stratigraphicl_bottom_depth_id_34d44d29_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	drilling_id integer not null
		constraint gwml2_stratigraphicl_drilling_id_e311dd93_fk_gwml2_dri
			references gwml2_drilling
				deferrable initially deferred,
	top_depth_id integer
		constraint gwml2_stratigraphiclog_top_depth_id_key
			unique
		constraint gwml2_stratigraphicl_top_depth_id_7cbfae47_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

create index if not exists gwml2_stratigraphiclog_drilling_id_e311dd93
	on gwml2_stratigraphiclog (drilling_id);

create table if not exists gwml2_screen
(
	id serial not null
		constraint gwml2_screen_pkey
			primary key,
	material varchar(512),
	description text,
	bottom_depth_id integer
		constraint gwml2_screen_bottom_depth_id_key
			unique
		constraint gwml2_screen_bottom_depth_id_5496a4f0_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	construction_id integer
		constraint gwml2_screen_construction_id_dd7cf252_fk_gwml2_construction_id
			references gwml2_construction
				deferrable initially deferred,
	diameter_id integer
		constraint gwml2_screen_diameter_id_key
			unique
		constraint gwml2_screen_diameter_id_fcabd88d_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	top_depth_id integer
		constraint gwml2_screen_top_depth_id_key
			unique
		constraint gwml2_screen_top_depth_id_21a5ae35_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

create index if not exists gwml2_screen_construction_id_dd7cf252
	on gwml2_screen (construction_id);

create table if not exists gwml2_pumpingtest
(
	id serial not null
		constraint gwml2_pumpingtest_pkey
			primary key,
	porosity double precision,
	storativity double precision,
	test_type varchar(512),
	hydraulic_conductivity_id integer
		constraint gwml2_pumpingtest_hydraulic_conductivity_id_key
			unique
		constraint gwml2_pumpingtest_hydraulic_conductivi_6a740938_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	specific_capacity_id integer
		constraint gwml2_pumpingtest_specific_capacity_id_key
			unique
		constraint gwml2_pumpingtest_specific_capacity_id_a325678c_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	specific_storage_id integer
		constraint gwml2_pumpingtest_specific_storage_id_key
			unique
		constraint gwml2_pumpingtest_specific_storage_id_a7192f13_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	transmissivity_id integer
		constraint gwml2_pumpingtest_transmissivity_id_key
			unique
		constraint gwml2_pumpingtest_transmissivity_id_fdbe8722_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

create table if not exists gwml2_hydrogeologyparameter
(
	id serial not null
		constraint gwml2_hydrogeologyparameter_pkey
			primary key,
	aquifer_name varchar(512),
	aquifer_material varchar(512),
	aquifer_type_id integer
		constraint gwml2_hydrogeologypa_aquifer_type_id_635dd083_fk_gwml2_ter
			references gwml2_termaquifertype
				deferrable initially deferred,
	confinement_id integer
		constraint gwml2_hydrogeologypa_confinement_id_abd91009_fk_gwml2_ter
			references gwml2_termconfinement
				deferrable initially deferred,
	pumping_test_id integer
		constraint gwml2_hydrogeologyparameter_pumping_test_id_key
			unique
		constraint gwml2_hydrogeologypa_pumping_test_id_3480ee6f_fk_gwml2_pum
			references gwml2_pumpingtest
				deferrable initially deferred,
	thickness_id integer
		constraint gwml2_hydrogeologyparameter_thickness_id_key
			unique
		constraint gwml2_hydrogeologypa_thickness_id_e69a42e2_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

create index if not exists gwml2_hydrogeologyparameter_aquifer_type_id_635dd083
	on gwml2_hydrogeologyparameter (aquifer_type_id);

create index if not exists gwml2_hydrogeologyparameter_confinement_id_abd91009
	on gwml2_hydrogeologyparameter (confinement_id);

create table if not exists gwml2_well
(
	id serial not null
		constraint gwml2_well_pkey
			primary key,
	name varchar(512),
	location geometry(Point,4326) not null,
	address text,
	photo varchar(100),
	description text,
	original_id varchar(256) not null
		constraint gwml2_well_original_id_key
			unique,
	construction_id integer
		constraint gwml2_well_construction_id_key
			unique
		constraint gwml2_well_construction_id_5f4075e0_fk_gwml2_construction_id
			references gwml2_construction
				deferrable initially deferred,
	country_id integer
		constraint gwml2_well_country_id_071b4bfa_fk_gwml2_country_id
			references gwml2_country
				deferrable initially deferred,
	drilling_id integer
		constraint gwml2_well_drilling_id_key
			unique
		constraint gwml2_well_drilling_id_89f15c39_fk_gwml2_drilling_id
			references gwml2_drilling
				deferrable initially deferred,
	elevation_id integer
		constraint gwml2_well_elevation_id_key
			unique
		constraint gwml2_well_elevation_id_ad8cb551_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	feature_type_id integer
		constraint gwml2_well_feature_type_id_96584cdd_fk_gwml2_termfeaturetype_id
			references gwml2_termfeaturetype
				deferrable initially deferred,
	groundwater_level_id integer
		constraint gwml2_well_groundwater_level_id_key
			unique
		constraint gwml2_well_groundwater_level_id_b4dac022_fk_gwml2_wel
			references gwml2_wellgroundwaterlevel
				deferrable initially deferred,
	hydrogeology_parameter_id integer
		constraint gwml2_well_hydrogeology_parameter_id_key
			unique
		constraint gwml2_well_hydrogeology_paramet_68b0e327_fk_gwml2_hyd
			references gwml2_hydrogeologyparameter
				deferrable initially deferred,
	management_id integer
		constraint gwml2_well_management_id_key
			unique
		constraint gwml2_well_management_id_f48db7d0_fk_gwml2_management_id
			references gwml2_management
				deferrable initially deferred,
	purpose_id integer
		constraint gwml2_well_purpose_id_fd964624_fk_gwml2_termwellpurpose_id
			references gwml2_termwellpurpose
				deferrable initially deferred
);

create index if not exists gwml2_well_location_id
	on gwml2_well (location);

create index if not exists gwml2_well_original_id_b0dede1e_like
	on gwml2_well (original_id);

create index if not exists gwml2_well_country_id_071b4bfa
	on gwml2_well (country_id);

create index if not exists gwml2_well_feature_type_id_96584cdd
	on gwml2_well (feature_type_id);

create index if not exists gwml2_well_purpose_id_fd964624
	on gwml2_well (purpose_id);

create table if not exists gwml2_welldocument
(
	id serial not null
		constraint gwml2_welldocument_pkey
			primary key,
	uploaded_at timestamp with time zone not null,
	file varchar(100),
	file_path varchar(512),
	description text,
	well_id integer not null
		constraint gwml2_welldocument_well_id_93ae8820_fk_gwml2_well_id
			references gwml2_well
				deferrable initially deferred
);

create index if not exists gwml2_welldocument_well_id_93ae8820
	on gwml2_welldocument (well_id);

create table if not exists gwml2_measurement
(
	id serial not null
		constraint gwml2_measurement_pkey
			primary key,
	time timestamp with time zone,
	methodology varchar(512),
	parameter_id integer
		constraint gwml2_measurement_parameter_id_a851fa74_fk_gwml2_ter
			references gwml2_termmeasurementparameter
				deferrable initially deferred,
	quality_id integer
		constraint gwml2_measurement_quality_id_key
			unique
		constraint gwml2_measurement_quality_id_85ea7dcc_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

create index if not exists gwml2_measurement_parameter_id_a851fa74
	on gwml2_measurement (parameter_id);

create table if not exists gwml2_casing
(
	id serial not null
		constraint gwml2_casing_pkey
			primary key,
	material varchar(512),
	description text,
	bottom_depth_id integer
		constraint gwml2_casing_bottom_depth_id_key
			unique
		constraint gwml2_casing_bottom_depth_id_b89a35ce_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	construction_id integer
		constraint gwml2_casing_construction_id_f9822b37_fk_gwml2_construction_id
			references gwml2_construction
				deferrable initially deferred,
	diameter_id integer
		constraint gwml2_casing_diameter_id_key
			unique
		constraint gwml2_casing_diameter_id_f35bead7_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	top_depth_id integer
		constraint gwml2_casing_top_depth_id_key
			unique
		constraint gwml2_casing_top_depth_id_38485de9_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

create index if not exists gwml2_casing_construction_id_f9822b37
	on gwml2_casing (construction_id);

create table if not exists gwml2_wellyieldmeasurement
(
	measurement_ptr_id integer not null
		constraint gwml2_wellyieldmeasurement_pkey
			primary key
		constraint gwml2_wellyieldmeasu_measurement_ptr_id_567935c9_fk_gwml2_mea
			references gwml2_measurement
				deferrable initially deferred,
	well_id integer not null
		constraint gwml2_wellyieldmeasurement_well_id_5963e719_fk_gwml2_well_id
			references gwml2_well
				deferrable initially deferred
);

create index if not exists gwml2_wellyieldmeasurement_well_id_5963e719
	on gwml2_wellyieldmeasurement (well_id);

create table if not exists gwml2_wellqualitymeasurement
(
	measurement_ptr_id integer not null
		constraint gwml2_wellqualitymeasurement_pkey
			primary key
		constraint gwml2_wellqualitymea_measurement_ptr_id_3c7a5a2e_fk_gwml2_mea
			references gwml2_measurement
				deferrable initially deferred,
	well_id integer not null
		constraint gwml2_wellqualitymeasurement_well_id_973b6d82_fk_gwml2_well_id
			references gwml2_well
				deferrable initially deferred
);

create index if not exists gwml2_wellqualitymeasurement_well_id_973b6d82
	on gwml2_wellqualitymeasurement (well_id);

create table if not exists gwml2_wellgroundwaterlevelmeasurement
(
	measurement_ptr_id integer not null
		constraint gwml2_wellgroundwaterlevelmeasurement_pkey
			primary key
		constraint gwml2_wellgroundwate_measurement_ptr_id_b7a3cabc_fk_gwml2_mea
			references gwml2_measurement
				deferrable initially deferred,
	groundwater_level_id integer not null
		constraint gwml2_wellgroundwate_groundwater_level_id_96a71c51_fk_gwml2_wel
			references gwml2_wellgroundwaterlevel
				deferrable initially deferred
);

create index if not exists gwml2_wellgroundwaterlevel_groundwater_level_id_96a71c51
	on gwml2_wellgroundwaterlevelmeasurement (groundwater_level_id);

