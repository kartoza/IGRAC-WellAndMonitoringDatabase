create table if not exists country
(
	id serial not null
		constraint country_pkey
			primary key,
	name varchar(512) not null,
	code varchar(126) not null,
	geometry geometry(MultiPolygon,4326)
);

create index if not exists country_geometry_id
	on country (geometry);

create table if not exists license
(
	id serial not null
		constraint license_pkey
			primary key,
	number varchar(512),
	valid_from date,
	valid_until date,
	description text
);


create table if not exists term_aquifer_type
(
	id serial not null
		constraint term_aquifer_type_pkey
			primary key,
	name varchar(512) not null
		constraint term_aquifer_type_name_key
			unique,
	description text
);


create index if not exists term_aquifer_type_name_b3c03cca_like
	on term_aquifer_type (name);

create table if not exists term_confinement
(
	id serial not null
		constraint term_confinement_pkey
			primary key,
	name varchar(512) not null
		constraint term_confinement_name_key
			unique,
	description text
);

create index if not exists term_confinement_name_431548b1_like
	on term_confinement (name);

create table if not exists term_drilling_method
(
	id serial not null
		constraint term_drilling_method_pkey
			primary key,
	name varchar(512) not null
		constraint term_drilling_method_name_key
			unique,
	description text
);

create index if not exists term_drilling_method_name_f4395425_like
	on term_drilling_method (name);

create table if not exists term_feature_type
(
	id serial not null
		constraint term_feature_type_pkey
			primary key,
	name varchar(512) not null
		constraint term_feature_type_name_key
			unique,
	description text
);


create index if not exists term_feature_type_name_e29b2ace_like
	on term_feature_type (name);

create table if not exists term_groundwater_use
(
	id serial not null
		constraint term_groundwater_use_pkey
			primary key,
	name varchar(512) not null
		constraint term_groundwater_use_name_key
			unique,
	description text
);

create table if not exists management
(
	id serial not null
		constraint management_pkey
			primary key,
	manager varchar(512),
	description text,
	number_of_users integer,
	groundwater_use_id integer
		constraint management_groundwater_use_id_6fdc7a87_fk_term_grou
			references term_groundwater_use
				deferrable initially deferred,
	license_id integer
		constraint management_license_id_52bb7a2b_fk_license_id
			references license
				deferrable initially deferred
);

create index if not exists management_groundwater_use_id_6fdc7a87
	on management (groundwater_use_id);

create index if not exists management_license_id_52bb7a2b
	on management (license_id);

create index if not exists term_groundwater_use_name_1c3b9b41_like
	on term_groundwater_use (name);

create table if not exists term_measurement_parameter
(
	id serial not null
		constraint term_measurement_parameter_pkey
			primary key,
	name varchar(512) not null
		constraint term_measurement_parameter_name_key
			unique,
	description text
);

create index if not exists term_measurement_parameter_name_d089bb89_like
	on term_measurement_parameter (name);

create table if not exists term_well_purpose
(
	id serial not null
		constraint term_well_purpose_pkey
			primary key,
	name varchar(512) not null
		constraint term_well_purpose_name_key
			unique,
	description text
);

create index if not exists term_well_purpose_name_f3e58a01_like
	on term_well_purpose (name);

create table if not exists unit
(
	id serial not null
		constraint unit_pkey
			primary key,
	name varchar(512) not null
		constraint unit_name_key
			unique,
	description text,
	html varchar(512)
);

create table if not exists quantity
(
	id serial not null
		constraint quantity_pkey
			primary key,
	value double precision not null,
	unit_id integer
		constraint quantity_unit_id_038af01a_fk_unit_id
			references unit
				deferrable initially deferred
);

create table if not exists geology
(
	id serial not null
		constraint geology_pkey
			primary key,
	total_depth_id integer
		constraint geology_total_depth_id_key
			unique
		constraint geology_total_depth_id_544fd8ca_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create index if not exists quantity_unit_id_038af01a
	on quantity (unit_id);

create table if not exists reference_elevation
(
	id serial not null
		constraint reference_elevation_pkey
			primary key,
	description text,
	value_id integer
		constraint reference_elevation_value_id_key
			unique
		constraint reference_elevation_value_id_3f05f3de_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create table if not exists construction
(
	id serial not null
		constraint construction_pkey
			primary key,
	pump_installer varchar(512),
	pump_description text,
	reference_elevation_id integer
		constraint construction_reference_elevation_id_key
			unique
		constraint construction_reference_elevation__7c172a2f_fk_reference
			references reference_elevation
				deferrable initially deferred
);

create table if not exists drilling
(
	id serial not null
		constraint drilling_pkey
			primary key,
	driller varchar(512),
	successful boolean,
	failed_explanation text,
	drilling_method_id integer
		constraint drilling_drilling_method_id_1ea6d064_fk_term_drilling_method_id
			references term_drilling_method
				deferrable initially deferred,
	reference_elevation_id integer
		constraint drilling_reference_elevation_id_key
			unique
		constraint drilling_reference_elevation__fbdbea8e_fk_reference
			references reference_elevation
				deferrable initially deferred,
	total_depth_id integer
		constraint drilling_total_depth_id_key
			unique
		constraint drilling_total_depth_id_99f4ad05_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create index if not exists drilling_drilling_method_id_1ea6d064
	on drilling (drilling_method_id);

create index if not exists unit_name_0fb28e2c_like
	on unit (name);

create table if not exists well_groundwater_level
(
	id serial not null
		constraint well_groundwater_level_pkey
			primary key,
	reference_elevation_id integer
		constraint well_groundwater_level_reference_elevation_id_key
			unique
		constraint well_groundwater_lev_reference_elevation__8a062190_fk_reference
			references reference_elevation
				deferrable initially deferred
);

create table if not exists well_groundwater_level_measurement
(
	id serial not null
		constraint well_groundwater_level_measurement_pkey
			primary key,
	time timestamp with time zone,
	methodology varchar(512),
	groundwater_level_id integer not null
		constraint well_groundwater_lev_groundwater_level_id_b327694d_fk_well_grou
			references well_groundwater_level
				deferrable initially deferred,
	parameter_id integer
		constraint well_groundwater_lev_parameter_id_7fdc040e_fk_term_meas
			references term_measurement_parameter
				deferrable initially deferred,
	quality_id integer
		constraint well_groundwater_level_measurement_quality_id_key
			unique
		constraint well_groundwater_lev_quality_id_1bb72223_fk_quantity_
			references quantity
				deferrable initially deferred
);

create index if not exists well_groundwater_level_mea_groundwater_level_id_b327694d
	on well_groundwater_level_measurement (groundwater_level_id);

create index if not exists well_groundwater_level_measurement_parameter_id_7fdc040e
	on well_groundwater_level_measurement (parameter_id);

create table if not exists drilling_water_strike
(
	id serial not null
		constraint drilling_water_strike_pkey
			primary key,
	description text,
	depth_id integer
		constraint drilling_water_strike_depth_id_key
			unique
		constraint drilling_water_strike_depth_id_bf747eef_fk_quantity_id
			references quantity
				deferrable initially deferred,
	drilling_id integer
		constraint drilling_water_strike_drilling_id_c0e2afde_fk_drilling_id
			references drilling
				deferrable initially deferred
);

create index if not exists drilling_water_strike_drilling_id_c0e2afde
	on drilling_water_strike (drilling_id);

create table if not exists unit_group
(
	id serial not null
		constraint unit_group_pkey
			primary key,
	name varchar(512) not null
		constraint unit_group_name_key
			unique,
	description text
);

create index if not exists unit_group_name_fb47141c_like
	on unit_group (name);

create table if not exists unit_group_units
(
	id serial not null
		constraint unit_group_units_pkey
			primary key,
	unitgroup_id integer not null
		constraint unit_group_units_unitgroup_id_ef84aa28_fk_unit_group_id
			references unit_group
				deferrable initially deferred,
	unit_id integer not null
		constraint unit_group_units_unit_id_2745a45d_fk_unit_id
			references unit
				deferrable initially deferred,
	constraint unit_group_units_unitgroup_id_unit_id_dbc68481_uniq
		unique (unitgroup_id, unit_id)
);

create index if not exists unit_group_units_unitgroup_id_ef84aa28
	on unit_group_units (unitgroup_id);

create index if not exists unit_group_units_unit_id_2745a45d
	on unit_group_units (unit_id);

create table if not exists drilling_stratigraphic_log
(
	id serial not null
		constraint drilling_stratigraphic_log_pkey
			primary key,
	material varchar(512),
	stratigraphic_unit varchar(256),
	bottom_depth_id integer
		constraint drilling_stratigraphic_log_bottom_depth_id_key
			unique
		constraint drilling_stratigraph_bottom_depth_id_4872c3fa_fk_quantity_
			references quantity
				deferrable initially deferred,
	drilling_id integer not null
		constraint drilling_stratigraphic_log_drilling_id_4984e810_fk_drilling_id
			references drilling
				deferrable initially deferred,
	top_depth_id integer
		constraint drilling_stratigraphic_log_top_depth_id_key
			unique
		constraint drilling_stratigraphic_log_top_depth_id_5d7f5a5b_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create index if not exists drilling_stratigraphic_log_drilling_id_4984e810
	on drilling_stratigraphic_log (drilling_id);

create table if not exists construction_screen
(
	id serial not null
		constraint construction_screen_pkey
			primary key,
	material varchar(512),
	description text,
	bottom_depth_id integer
		constraint construction_screen_bottom_depth_id_key
			unique
		constraint construction_screen_bottom_depth_id_c9bc66d0_fk_quantity_id
			references quantity
				deferrable initially deferred,
	construction_id integer
		constraint construction_screen_construction_id_5f0c50fc_fk_construction_id
			references construction
				deferrable initially deferred,
	diameter_id integer
		constraint construction_screen_diameter_id_key
			unique
		constraint construction_screen_diameter_id_48b9a29e_fk_quantity_id
			references quantity
				deferrable initially deferred,
	top_depth_id integer
		constraint construction_screen_top_depth_id_key
			unique
		constraint construction_screen_top_depth_id_8698874e_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create index if not exists construction_screen_construction_id_5f0c50fc
	on construction_screen (construction_id);

create table if not exists pumping_test
(
	id serial not null
		constraint pumping_test_pkey
			primary key,
	porosity double precision,
	specific_yield double precision,
	storativity double precision,
	test_type varchar(512),
	hydraulic_conductivity_id integer
		constraint pumping_test_hydraulic_conductivity_id_key
			unique
		constraint pumping_test_hydraulic_conductivity_id_33c13e29_fk_quantity_id
			references quantity
				deferrable initially deferred,
	specific_capacity_id integer
		constraint pumping_test_specific_capacity_id_key
			unique
		constraint pumping_test_specific_capacity_id_f85b2eb1_fk_quantity_id
			references quantity
				deferrable initially deferred,
	specific_storage_id integer
		constraint pumping_test_specific_storage_id_key
			unique
		constraint pumping_test_specific_storage_id_b3d30f05_fk_quantity_id
			references quantity
				deferrable initially deferred,
	transmissivity_id integer
		constraint pumping_test_transmissivity_id_key
			unique
		constraint pumping_test_transmissivity_id_4339a0a8_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create table if not exists hydrogeology_parameter
(
	id serial not null
		constraint hydrogeology_parameter_pkey
			primary key,
	aquifer_name varchar(512),
	aquifer_material varchar(512),
	degree_of_confinement double precision,
	aquifer_thickness_id integer
		constraint hydrogeology_parameter_aquifer_thickness_id_key
			unique
		constraint hydrogeology_paramet_aquifer_thickness_id_2c3e6277_fk_quantity_
			references quantity
				deferrable initially deferred,
	aquifer_type_id integer
		constraint hydrogeology_paramet_aquifer_type_id_d43a3953_fk_term_aqui
			references term_aquifer_type
				deferrable initially deferred,
	confinement_id integer
		constraint hydrogeology_paramet_confinement_id_6dcfac58_fk_term_conf
			references term_confinement
				deferrable initially deferred,
	pumping_test_id integer
		constraint hydrogeology_parameter_pumping_test_id_key
			unique
		constraint hydrogeology_paramet_pumping_test_id_f7dfd3a8_fk_pumping_t
			references pumping_test
				deferrable initially deferred
);

create index if not exists hydrogeology_parameter_aquifer_type_id_d43a3953
	on hydrogeology_parameter (aquifer_type_id);

create index if not exists hydrogeology_parameter_confinement_id_6dcfac58
	on hydrogeology_parameter (confinement_id);

create table if not exists well
(
	id serial not null
		constraint well_pkey
			primary key,
	name varchar(512),
	location geometry(Point,4326) not null,
	address text,
	photo varchar(100),
	description text,
	original_id varchar(256) not null
		constraint well_original_id_key
			unique,
	construction_id integer
		constraint well_construction_id_key
			unique
		constraint well_construction_id_cc72fb69_fk_construction_id
			references construction
				deferrable initially deferred,
	country_id integer
		constraint well_country_id_3c527bfa_fk_country_id
			references country
				deferrable initially deferred,
	drilling_id integer
		constraint well_drilling_id_key
			unique
		constraint well_drilling_id_38250d8d_fk_drilling_id
			references drilling
				deferrable initially deferred,
	elevation_id integer
		constraint well_elevation_id_key
			unique
		constraint well_elevation_id_91aa9545_fk_quantity_id
			references quantity
				deferrable initially deferred,
	feature_type_id integer
		constraint well_feature_type_id_805bb0ab_fk_term_feature_type_id
			references term_feature_type
				deferrable initially deferred,
	geology_id integer
		constraint well_geology_id_key
			unique
		constraint well_geology_id_0dbaeba7_fk_geology_id
			references geology
				deferrable initially deferred,
	groundwater_level_id integer
		constraint well_groundwater_level_id_key
			unique
		constraint well_groundwater_level_id_4a2feb7e_fk_well_groundwater_level_id
			references well_groundwater_level
				deferrable initially deferred,
	hydrogeology_parameter_id integer
		constraint well_hydrogeology_parameter_id_key
			unique
		constraint well_hydrogeology_paramet_0958e7d7_fk_hydrogeol
			references hydrogeology_parameter
				deferrable initially deferred,
	management_id integer
		constraint well_management_id_key
			unique
		constraint well_management_id_0a447d6c_fk_management_id
			references management
				deferrable initially deferred,
	purpose_id integer
		constraint well_purpose_id_77b5b9ae_fk_term_well_purpose_id
			references term_well_purpose
				deferrable initially deferred
);

create index if not exists well_location_id
	on well (location);

create index if not exists well_original_id_be895903_like
	on well (original_id);

create index if not exists well_country_id_3c527bfa
	on well (country_id);

create index if not exists well_feature_type_id_805bb0ab
	on well (feature_type_id);

create index if not exists well_purpose_id_77b5b9ae
	on well (purpose_id);

create table if not exists well_yield_measurement
(
	id serial not null
		constraint well_yield_measurement_pkey
			primary key,
	time timestamp with time zone,
	methodology varchar(512),
	parameter_id integer
		constraint well_yield_measureme_parameter_id_5cae313b_fk_term_meas
			references term_measurement_parameter
				deferrable initially deferred,
	quality_id integer
		constraint well_yield_measurement_quality_id_key
			unique
		constraint well_yield_measurement_quality_id_32ee805a_fk_quantity_id
			references quantity
				deferrable initially deferred,
	well_id integer not null
		constraint well_yield_measurement_well_id_7510f79a_fk_well_id
			references well
				deferrable initially deferred
);

create index if not exists well_yield_measurement_parameter_id_5cae313b
	on well_yield_measurement (parameter_id);

create index if not exists well_yield_measurement_well_id_7510f79a
	on well_yield_measurement (well_id);

create table if not exists well_quality_measurement
(
	id serial not null
		constraint well_quality_measurement_pkey
			primary key,
	time timestamp with time zone,
	methodology varchar(512),
	parameter_id integer
		constraint well_quality_measure_parameter_id_dcd2af39_fk_term_meas
			references term_measurement_parameter
				deferrable initially deferred,
	quality_id integer
		constraint well_quality_measurement_quality_id_key
			unique
		constraint well_quality_measurement_quality_id_f16bf103_fk_quantity_id
			references quantity
				deferrable initially deferred,
	well_id integer not null
		constraint well_quality_measurement_well_id_9f974c46_fk_well_id
			references well
				deferrable initially deferred
);

create index if not exists well_quality_measurement_parameter_id_dcd2af39
	on well_quality_measurement (parameter_id);

create index if not exists well_quality_measurement_well_id_9f974c46
	on well_quality_measurement (well_id);

create table if not exists well_document
(
	id serial not null
		constraint well_document_pkey
			primary key,
	uploaded_at timestamp with time zone not null,
	file varchar(100),
	file_path varchar(512),
	description text,
	well_id integer not null
		constraint well_document_well_id_b66b28a1_fk_well_id
			references well
				deferrable initially deferred
);

create index if not exists well_document_well_id_b66b28a1
	on well_document (well_id);

create table if not exists construction_casing
(
	id serial not null
		constraint construction_casing_pkey
			primary key,
	material varchar(512),
	description text,
	bottom_depth_id integer
		constraint construction_casing_bottom_depth_id_key
			unique
		constraint construction_casing_bottom_depth_id_82bb56ce_fk_quantity_id
			references quantity
				deferrable initially deferred,
	construction_id integer
		constraint construction_casing_construction_id_07a0f107_fk_construction_id
			references construction
				deferrable initially deferred,
	diameter_id integer
		constraint construction_casing_diameter_id_key
			unique
		constraint construction_casing_diameter_id_b38fc20f_fk_quantity_id
			references quantity
				deferrable initially deferred,
	top_depth_id integer
		constraint construction_casing_top_depth_id_key
			unique
		constraint construction_casing_top_depth_id_2d958965_fk_quantity_id
			references quantity
				deferrable initially deferred
);

create index if not exists construction_casing_construction_id_07a0f107
	on construction_casing (construction_id);

