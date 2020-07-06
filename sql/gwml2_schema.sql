begin;

create table if not exists spatial_ref_sys
(
	srid integer not null
		constraint spatial_ref_sys_pkey
			primary key
		constraint spatial_ref_sys_srid_check
			check ((srid > 0) AND (srid <= 998999)),
	auth_name varchar(256),
	auth_srid integer,
	srtext varchar(2048),
	proj4text varchar(2048)
);

alter table spatial_ref_sys owner to postgres;

create table if not exists django_migrations
(
	id serial not null
		constraint django_migrations_pkey
			primary key,
	app varchar(255) not null,
	name varchar(255) not null,
	applied timestamp with time zone not null
);

alter table django_migrations owner to geonode;

create table if not exists gwml2_bodyqualitytype
(
	id serial not null
		constraint gwml2_bodyqualitytype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_bodyqualitytype owner to geonode;

create table if not exists gwml2_casingcoatingterm
(
	id serial not null
		constraint gwml2_casingcoatingterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_casingcoatingterm owner to geonode;

create table if not exists gwml2_casingformterm
(
	id serial not null
		constraint gwml2_casingformterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_casingformterm owner to geonode;

create table if not exists gwml2_casingmaterialterm
(
	id serial not null
		constraint gwml2_casingmaterialterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_casingmaterialterm owner to geonode;

create table if not exists gwml2_filtrationmaterialterm
(
	id serial not null
		constraint gwml2_filtrationmaterialterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_filtrationmaterialterm owner to geonode;

create table if not exists gwml2_gwlicence
(
	id serial not null
		constraint gwml2_gwlicence_pkey
			primary key,
	gw_licence_id varchar(150) not null,
	gw_purpose text not null,
	gw_associated_gw_volume double precision,
	gw_time_period timestamp with time zone
);

alter table gwml2_gwlicence owner to geonode;

create table if not exists gwml2_gwmetadata
(
	id serial not null
		constraint gwml2_gwmetadata_pkey
			primary key,
	text text not null
);

alter table gwml2_gwmetadata owner to geonode;

create table if not exists gwml2_quantity
(
	id serial not null
		constraint gwml2_quantity_pkey
			primary key,
	unit text,
	value double precision
);

alter table gwml2_quantity owner to geonode;

create table if not exists gwml2_constructioncomponent
(
	id serial not null
		constraint gwml2_constructioncomponent_pkey
			primary key,
	"from" integer
		constraint gwml2_constructioncomponent_from_key
			unique
		constraint gwml2_constructioncomponent_from_21f16fa8_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	"to" integer
		constraint gwml2_constructioncomponent_to_key
			unique
		constraint gwml2_constructioncomponent_to_69f00033_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_constructioncomponent owner to geonode;

create table if not exists gwml2_sealingmaterialterm
(
	id serial not null
		constraint gwml2_sealingmaterialterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_sealingmaterialterm owner to geonode;

create table if not exists gwml2_sealingtypeterm
(
	id serial not null
		constraint gwml2_sealingtypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_sealingtypeterm owner to geonode;

create table if not exists gwml2_vulnerabilitytype
(
	id serial not null
		constraint gwml2_vulnerabilitytype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_vulnerabilitytype owner to geonode;

create table if not exists gwml2_wellstatustypeterm
(
	id serial not null
		constraint gwml2_wellstatustypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_wellstatustypeterm owner to geonode;

create table if not exists gwml2_sealingcomponent
(
	id serial not null
		constraint gwml2_sealingcomponent_pkey
			primary key,
	sealing_material_id integer
		constraint gwml2_sealingcompone_sealing_material_id_822d6521_fk_gwml2_sea
			references gwml2_sealingmaterialterm
				deferrable initially deferred,
	sealing_type_id integer
		constraint gwml2_sealingcompone_sealing_type_id_5b273dd5_fk_gwml2_sea
			references gwml2_sealingtypeterm
				deferrable initially deferred
);

alter table gwml2_sealingcomponent owner to geonode;

create index if not exists gwml2_sealingcomponent_sealing_material_id_822d6521
	on gwml2_sealingcomponent (sealing_material_id);

create index if not exists gwml2_sealingcomponent_sealing_type_id_5b273dd5
	on gwml2_sealingcomponent (sealing_type_id);

create table if not exists gwml2_gwvulnerability
(
	id serial not null
		constraint gwml2_gwvulnerability_pkey
			primary key,
	gw_vulnerability_id integer
		constraint gwml2_gwvulnerability_gw_vulnerability_id_key
			unique
		constraint gwml2_gwvulnerabilit_gw_vulnerability_id_9d5eca78_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_vulnerability_type_id integer
		constraint gwml2_gwvulnerabilit_gw_vulnerability_typ_66d87f7c_fk_gwml2_vul
			references gwml2_vulnerabilitytype
				deferrable initially deferred
);

alter table gwml2_gwvulnerability owner to geonode;

create index if not exists gwml2_gwvulnerability_gw_vulnerability_type_id_66d87f7c
	on gwml2_gwvulnerability (gw_vulnerability_type_id);

create table if not exists gwml2_gwfluidbody
(
	id serial not null
		constraint gwml2_gwfluidbody_pkey
			primary key,
	gw_body_description text,
	gw_body_shape geometry(Geometry,4326),
	gw_body_volume_id integer
		constraint gwml2_gwfluidbody_gw_body_volume_id_key
			unique
		constraint gwml2_gwfluidbody_gw_body_volume_id_2b19befb_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_part_of_body_id integer
		constraint gwml2_gwfluidbody_gw_part_of_body_id_e6bc796e_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred
);

alter table gwml2_gwfluidbody owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_shape_id
	on gwml2_gwfluidbody (gw_body_shape);

create index if not exists gwml2_gwfluidbody_gw_part_of_body_id_e6bc796e
	on gwml2_gwfluidbody (gw_part_of_body_id);

create table if not exists gwml2_gwfluidbody_gw_body_metadata
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_metadata_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_12318846_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwmetadata_id integer not null
		constraint gwml2_gwfluidbody_gw_gwmetadata_id_bc996af4_fk_gwml2_gwm
			references gwml2_gwmetadata
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_gwmetadat_41155b90_uniq
		unique (gwfluidbody_id, gwmetadata_id)
);

alter table gwml2_gwfluidbody_gw_body_metadata owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_metadata_gwfluidbody_id_12318846
	on gwml2_gwfluidbody_gw_body_metadata (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body_metadata_gwmetadata_id_bc996af4
	on gwml2_gwfluidbody_gw_body_metadata (gwmetadata_id);

create table if not exists gwml2_gwfluidbody_gw_body_quality
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_quality_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_181de722_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	bodyqualitytype_id integer not null
		constraint gwml2_gwfluidbody_gw_bodyqualitytype_id_66bc2525_fk_gwml2_bod
			references gwml2_bodyqualitytype
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_bodyquali_22b6f01c_uniq
		unique (gwfluidbody_id, bodyqualitytype_id)
);

alter table gwml2_gwfluidbody_gw_body_quality owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_quality_gwfluidbody_id_181de722
	on gwml2_gwfluidbody_gw_body_quality (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body_quality_bodyqualitytype_id_66bc2525
	on gwml2_gwfluidbody_gw_body_quality (bodyqualitytype_id);

create table if not exists gwml2_gwfluidbody_gw_body_vulnerability
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_vulnerability_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_72be5ed8_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwvulnerability_id integer not null
		constraint gwml2_gwfluidbody_gw_gwvulnerability_id_ee4dc4cb_fk_gwml2_gwv
			references gwml2_gwvulnerability
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_gwvulnera_afac7aec_uniq
		unique (gwfluidbody_id, gwvulnerability_id)
);

alter table gwml2_gwfluidbody_gw_body_vulnerability owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_vulnerability_gwfluidbody_id_72be5ed8
	on gwml2_gwfluidbody_gw_body_vulnerability (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body__gwvulnerability_id_ee4dc4cb
	on gwml2_gwfluidbody_gw_body_vulnerability (gwvulnerability_id);

create table if not exists gwml2_filtrationcomponent
(
	id serial not null
		constraint gwml2_filtrationcomponent_pkey
			primary key,
	construction_component_id integer
		constraint gwml2_filtrationcomp_construction_compone_f049221d_fk_gwml2_con
			references gwml2_constructioncomponent
				deferrable initially deferred,
	filter_grain_size_id integer
		constraint gwml2_filtrationcomponent_filter_grain_size_id_key
			unique
		constraint gwml2_filtrationcomp_filter_grain_size_id_a288ac99_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	filter_material_id integer
		constraint gwml2_filtrationcomp_filter_material_id_eeb956c6_fk_gwml2_fil
			references gwml2_filtrationmaterialterm
				deferrable initially deferred
);

alter table gwml2_filtrationcomponent owner to geonode;

create index if not exists gwml2_filtrationcomponent_construction_component_id_f049221d
	on gwml2_filtrationcomponent (construction_component_id);

create index if not exists gwml2_filtrationcomponent_filter_material_id_eeb956c6
	on gwml2_filtrationcomponent (filter_material_id);

create table if not exists gwml2_casingcomponent
(
	id serial not null
		constraint gwml2_casingcomponent_pkey
			primary key,
	casing_coating_id integer
		constraint gwml2_casingcomponen_casing_coating_id_25d6a87f_fk_gwml2_cas
			references gwml2_casingcoatingterm
				deferrable initially deferred,
	casing_external_diameter_id integer
		constraint gwml2_casingcomponent_casing_external_diameter_id_key
			unique
		constraint gwml2_casingcomponen_casing_external_diam_e6822702_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	casing_form_id integer
		constraint gwml2_casingcomponen_casing_form_id_c3b06618_fk_gwml2_cas
			references gwml2_casingformterm
				deferrable initially deferred,
	casing_internal_diameter_id integer
		constraint gwml2_casingcomponent_casing_internal_diameter_id_key
			unique
		constraint gwml2_casingcomponen_casing_internal_diam_d41f539e_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	casing_material_id integer
		constraint gwml2_casingcomponen_casing_material_id_8b105f76_fk_gwml2_cas
			references gwml2_casingmaterialterm
				deferrable initially deferred,
	casing_wall_thickness_id integer
		constraint gwml2_casingcomponent_casing_wall_thickness_id_key
			unique
		constraint gwml2_casingcomponen_casing_wall_thicknes_a4190e5f_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_casingcomponent owner to geonode;

create index if not exists gwml2_casingcomponent_casing_coating_id_25d6a87f
	on gwml2_casingcomponent (casing_coating_id);

create index if not exists gwml2_casingcomponent_casing_form_id_c3b06618
	on gwml2_casingcomponent (casing_form_id);

create index if not exists gwml2_casingcomponent_casing_material_id_8b105f76
	on gwml2_casingcomponent (casing_material_id);

create table if not exists gwml2_attachmentmethodterm
(
	id serial not null
		constraint gwml2_attachmentmethodterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_attachmentmethodterm owner to geonode;

create table if not exists gwml2_omprocess
(
	id serial not null
		constraint gwml2_omprocess_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_omprocess owner to geonode;

create table if not exists gwml2_perforationmethodterm
(
	id serial not null
		constraint gwml2_perforationmethodterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_perforationmethodterm owner to geonode;

create table if not exists gwml2_screencoatingterm
(
	id serial not null
		constraint gwml2_screencoatingterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screencoatingterm owner to geonode;

create table if not exists gwml2_screenfittingterm
(
	id serial not null
		constraint gwml2_screenfittingterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screenfittingterm owner to geonode;

create table if not exists gwml2_screenformterm
(
	id serial not null
		constraint gwml2_screenformterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screenformterm owner to geonode;

create table if not exists gwml2_screenmakerterm
(
	id serial not null
		constraint gwml2_screenmakerterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screenmakerterm owner to geonode;

create table if not exists gwml2_screenmaterialterm
(
	id serial not null
		constraint gwml2_screenmaterialterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screenmaterialterm owner to geonode;

create table if not exists gwml2_screenmodelterm
(
	id serial not null
		constraint gwml2_screenmodelterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screenmodelterm owner to geonode;

create table if not exists gwml2_screennumberterm
(
	id serial not null
		constraint gwml2_screennumberterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screennumberterm owner to geonode;

create table if not exists gwml2_screenplacementterm
(
	id serial not null
		constraint gwml2_screenplacementterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_screenplacementterm owner to geonode;

create table if not exists gwml2_sealing
(
	id serial not null
		constraint gwml2_sealing_pkey
			primary key,
	sealing_grouting_placement_method_id integer
		constraint gwml2_sealing_sealing_grouting_pla_2ac2b213_fk_gwml2_omp
			references gwml2_omprocess
				deferrable initially deferred
);

alter table gwml2_sealing owner to geonode;

create index if not exists gwml2_sealing_sealing_grouting_placement_method_id_2ac2b213
	on gwml2_sealing (sealing_grouting_placement_method_id);

create table if not exists gwml2_sealing_casing_left
(
	id serial not null
		constraint gwml2_sealing_casing_left_pkey
			primary key,
	sealing_id integer not null
		constraint gwml2_sealing_casing_sealing_id_6e47f5a2_fk_gwml2_sea
			references gwml2_sealing
				deferrable initially deferred,
	casingcomponent_id integer not null
		constraint gwml2_sealing_casing_casingcomponent_id_4a2f4592_fk_gwml2_cas
			references gwml2_casingcomponent
				deferrable initially deferred,
	constraint gwml2_sealing_casing_lef_sealing_id_casingcompone_82a27de7_uniq
		unique (sealing_id, casingcomponent_id)
);

alter table gwml2_sealing_casing_left owner to geonode;

create index if not exists gwml2_sealing_casing_left_sealing_id_6e47f5a2
	on gwml2_sealing_casing_left (sealing_id);

create index if not exists gwml2_sealing_casing_left_casingcomponent_id_4a2f4592
	on gwml2_sealing_casing_left (casingcomponent_id);

create table if not exists gwml2_sealing_casing_slit
(
	id serial not null
		constraint gwml2_sealing_casing_slit_pkey
			primary key,
	sealing_id integer not null
		constraint gwml2_sealing_casing_sealing_id_fde6b155_fk_gwml2_sea
			references gwml2_sealing
				deferrable initially deferred,
	casingcomponent_id integer not null
		constraint gwml2_sealing_casing_casingcomponent_id_9aa739e1_fk_gwml2_cas
			references gwml2_casingcomponent
				deferrable initially deferred,
	constraint gwml2_sealing_casing_sli_sealing_id_casingcompone_b755c903_uniq
		unique (sealing_id, casingcomponent_id)
);

alter table gwml2_sealing_casing_slit owner to geonode;

create index if not exists gwml2_sealing_casing_slit_sealing_id_fde6b155
	on gwml2_sealing_casing_slit (sealing_id);

create index if not exists gwml2_sealing_casing_slit_casingcomponent_id_9aa739e1
	on gwml2_sealing_casing_slit (casingcomponent_id);

create table if not exists gwml2_sealing_sealing_element
(
	id serial not null
		constraint gwml2_sealing_sealing_element_pkey
			primary key,
	sealing_id integer not null
		constraint gwml2_sealing_sealin_sealing_id_45390602_fk_gwml2_sea
			references gwml2_sealing
				deferrable initially deferred,
	sealingcomponent_id integer not null
		constraint gwml2_sealing_sealin_sealingcomponent_id_d7cbea7e_fk_gwml2_sea
			references gwml2_sealingcomponent
				deferrable initially deferred,
	constraint gwml2_sealing_sealing_el_sealing_id_sealingcompon_06619022_uniq
		unique (sealing_id, sealingcomponent_id)
);

alter table gwml2_sealing_sealing_element owner to geonode;

create index if not exists gwml2_sealing_sealing_element_sealing_id_45390602
	on gwml2_sealing_sealing_element (sealing_id);

create index if not exists gwml2_sealing_sealing_element_sealingcomponent_id_d7cbea7e
	on gwml2_sealing_sealing_element (sealingcomponent_id);

create table if not exists gwml2_screencomponent
(
	id serial not null
		constraint gwml2_screencomponent_pkey
			primary key,
	construction_component_id integer
		constraint gwml2_screencomponen_construction_compone_5e7bcf7d_fk_gwml2_con
			references gwml2_constructioncomponent
				deferrable initially deferred,
	screen_attachment_method_id integer
		constraint gwml2_screencomponen_screen_attachment_me_d5e1f545_fk_gwml2_att
			references gwml2_attachmentmethodterm
				deferrable initially deferred,
	screen_coating_id integer
		constraint gwml2_screencomponen_screen_coating_id_9b7978b9_fk_gwml2_scr
			references gwml2_screencoatingterm
				deferrable initially deferred,
	screen_external_diameter_id integer
		constraint gwml2_screencomponent_screen_external_diameter_id_key
			unique
		constraint gwml2_screencomponen_screen_external_diam_5892f09d_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	screen_fitting_id integer
		constraint gwml2_screencomponen_screen_fitting_id_383eb267_fk_gwml2_scr
			references gwml2_screenfittingterm
				deferrable initially deferred,
	screen_form_id integer
		constraint gwml2_screencomponen_screen_form_id_edc010ac_fk_gwml2_scr
			references gwml2_screenformterm
				deferrable initially deferred,
	screen_hole_size_id integer
		constraint gwml2_screencomponent_screen_hole_size_id_key
			unique
		constraint gwml2_screencomponen_screen_hole_size_id_c6f455c2_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	screen_internal_diameter_id integer
		constraint gwml2_screencomponent_screen_internal_diameter_id_key
			unique
		constraint gwml2_screencomponen_screen_internal_diam_61bac4b4_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	screen_make_id integer
		constraint gwml2_screencomponen_screen_make_id_0ed3dcfb_fk_gwml2_scr
			references gwml2_screenmakerterm
				deferrable initially deferred,
	screen_material_id integer
		constraint gwml2_screencomponen_screen_material_id_952d2161_fk_gwml2_scr
			references gwml2_screenmaterialterm
				deferrable initially deferred,
	screen_model_id integer
		constraint gwml2_screencomponen_screen_model_id_9857fd86_fk_gwml2_scr
			references gwml2_screenmodelterm
				deferrable initially deferred,
	screen_number_id integer
		constraint gwml2_screencomponen_screen_number_id_8f6925c2_fk_gwml2_scr
			references gwml2_screennumberterm
				deferrable initially deferred,
	screen_perforation_method_id integer
		constraint gwml2_screencomponen_screen_perforation_m_624d9db3_fk_gwml2_per
			references gwml2_perforationmethodterm
				deferrable initially deferred,
	screen_placement_id integer
		constraint gwml2_screencomponen_screen_placement_id_65ad23c7_fk_gwml2_scr
			references gwml2_screenplacementterm
				deferrable initially deferred,
	screen_wall_thickness_id integer
		constraint gwml2_screencomponent_screen_wall_thickness_id_key
			unique
		constraint gwml2_screencomponen_screen_wall_thicknes_3be85b85_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_screencomponent owner to geonode;

create index if not exists gwml2_screencomponent_construction_component_id_5e7bcf7d
	on gwml2_screencomponent (construction_component_id);

create index if not exists gwml2_screencomponent_screen_attachment_method_id_d5e1f545
	on gwml2_screencomponent (screen_attachment_method_id);

create index if not exists gwml2_screencomponent_screen_coating_id_9b7978b9
	on gwml2_screencomponent (screen_coating_id);

create index if not exists gwml2_screencomponent_screen_fitting_id_383eb267
	on gwml2_screencomponent (screen_fitting_id);

create index if not exists gwml2_screencomponent_screen_form_id_edc010ac
	on gwml2_screencomponent (screen_form_id);

create index if not exists gwml2_screencomponent_screen_make_id_0ed3dcfb
	on gwml2_screencomponent (screen_make_id);

create index if not exists gwml2_screencomponent_screen_material_id_952d2161
	on gwml2_screencomponent (screen_material_id);

create index if not exists gwml2_screencomponent_screen_model_id_9857fd86
	on gwml2_screencomponent (screen_model_id);

create index if not exists gwml2_screencomponent_screen_number_id_8f6925c2
	on gwml2_screencomponent (screen_number_id);

create index if not exists gwml2_screencomponent_screen_perforation_method_id_624d9db3
	on gwml2_screencomponent (screen_perforation_method_id);

create index if not exists gwml2_screencomponent_screen_placement_id_65ad23c7
	on gwml2_screencomponent (screen_placement_id);

create table if not exists gwml2_casing
(
	id serial not null
		constraint gwml2_casing_pkey
			primary key,
	name text
);

alter table gwml2_casing owner to geonode;

create table if not exists gwml2_casing_casing_element
(
	id serial not null
		constraint gwml2_casing_casing_element_pkey
			primary key,
	casing_id integer not null
		constraint gwml2_casing_casing__casing_id_1bba307a_fk_gwml2_cas
			references gwml2_casing
				deferrable initially deferred,
	casingcomponent_id integer not null
		constraint gwml2_casing_casing__casingcomponent_id_3023dd0d_fk_gwml2_cas
			references gwml2_casingcomponent
				deferrable initially deferred,
	constraint gwml2_casing_casing_elem_casing_id_casingcomponen_bdba05e0_uniq
		unique (casing_id, casingcomponent_id)
);

alter table gwml2_casing_casing_element owner to geonode;

create index if not exists gwml2_casing_casing_element_casing_id_1bba307a
	on gwml2_casing_casing_element (casing_id);

create index if not exists gwml2_casing_casing_element_casingcomponent_id_3023dd0d
	on gwml2_casing_casing_element (casingcomponent_id);

create table if not exists gwml2_filtration
(
	id serial not null
		constraint gwml2_filtration_pkey
			primary key,
	name text
);

alter table gwml2_filtration owner to geonode;

create table if not exists gwml2_filtration_filter_element
(
	id serial not null
		constraint gwml2_filtration_filter_element_pkey
			primary key,
	filtration_id integer not null
		constraint gwml2_filtration_fil_filtration_id_da3477ca_fk_gwml2_fil
			references gwml2_filtration
				deferrable initially deferred,
	filtrationcomponent_id integer not null
		constraint gwml2_filtration_fil_filtrationcomponent__3a56e3cb_fk_gwml2_fil
			references gwml2_filtrationcomponent
				deferrable initially deferred,
	constraint gwml2_filtration_filter__filtration_id_filtration_12be1e9e_uniq
		unique (filtration_id, filtrationcomponent_id)
);

alter table gwml2_filtration_filter_element owner to geonode;

create index if not exists gwml2_filtration_filter_element_filtration_id_da3477ca
	on gwml2_filtration_filter_element (filtration_id);

create index if not exists gwml2_filtration_filter_element_filtrationcomponent_id_3a56e3cb
	on gwml2_filtration_filter_element (filtrationcomponent_id);

create table if not exists gwml2_screen
(
	id serial not null
		constraint gwml2_screen_pkey
			primary key,
	name text
);

alter table gwml2_screen owner to geonode;

create table if not exists gwml2_screen_screen_element
(
	id serial not null
		constraint gwml2_screen_screen_element_pkey
			primary key,
	screen_id integer not null
		constraint gwml2_screen_screen__screen_id_1606b2e4_fk_gwml2_scr
			references gwml2_screen
				deferrable initially deferred,
	screencomponent_id integer not null
		constraint gwml2_screen_screen__screencomponent_id_c57a74a2_fk_gwml2_scr
			references gwml2_screencomponent
				deferrable initially deferred,
	constraint gwml2_screen_screen_elem_screen_id_screencomponen_cd4b4c1e_uniq
		unique (screen_id, screencomponent_id)
);

alter table gwml2_screen_screen_element owner to geonode;

create index if not exists gwml2_screen_screen_element_screen_id_1606b2e4
	on gwml2_screen_screen_element (screen_id);

create index if not exists gwml2_screen_screen_element_screencomponent_id_c57a74a2
	on gwml2_screen_screen_element (screencomponent_id);

create table if not exists gwml2_wellconstruction
(
	id serial not null
		constraint gwml2_wellconstruction_pkey
			primary key,
	name text,
	casing_id integer
		constraint gwml2_wellconstruction_casing_id_533ca759_fk_gwml2_casing_id
			references gwml2_casing
				deferrable initially deferred,
	filtration_id integer
		constraint gwml2_wellconstructi_filtration_id_3efc3925_fk_gwml2_fil
			references gwml2_filtration
				deferrable initially deferred,
	screen_id integer
		constraint gwml2_wellconstruction_screen_id_657bf8cf_fk_gwml2_screen_id
			references gwml2_screen
				deferrable initially deferred,
	sealing_id integer
		constraint gwml2_wellconstruction_sealing_id_cc747dab_fk_gwml2_sealing_id
			references gwml2_sealing
				deferrable initially deferred
);

alter table gwml2_wellconstruction owner to geonode;

create index if not exists gwml2_wellconstruction_casing_id_533ca759
	on gwml2_wellconstruction (casing_id);

create index if not exists gwml2_wellconstruction_filtration_id_3efc3925
	on gwml2_wellconstruction (filtration_id);

create index if not exists gwml2_wellconstruction_screen_id_657bf8cf
	on gwml2_wellconstruction (screen_id);

create index if not exists gwml2_wellconstruction_sealing_id_cc747dab
	on gwml2_wellconstruction (sealing_id);

create table if not exists gwml2_elevationmeasurementmethodtype
(
	id serial not null
		constraint gwml2_elevationmeasurementmethodtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_elevationmeasurementmethodtype owner to geonode;

create table if not exists gwml2_elevationtypeterm
(
	id serial not null
		constraint gwml2_elevationtypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_elevationtypeterm owner to geonode;

create table if not exists gwml2_positionalaccuracytype
(
	id serial not null
		constraint gwml2_positionalaccuracytype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_positionalaccuracytype owner to geonode;

create table if not exists gwml2_elevation
(
	id serial not null
		constraint gwml2_elevation_pkey
			primary key,
	elevation geometry(Point,4326) not null,
	elevation_accuracy_id integer
		constraint gwml2_elevation_elevation_accuracy_i_6afcf42d_fk_gwml2_pos
			references gwml2_positionalaccuracytype
				deferrable initially deferred,
	elevation_measurement_method_id integer
		constraint gwml2_elevation_elevation_measuremen_f22b8f3a_fk_gwml2_ele
			references gwml2_elevationmeasurementmethodtype
				deferrable initially deferred,
	elevation_type_id integer
		constraint gwml2_elevation_elevation_type_id_da9510a6_fk_gwml2_ele
			references gwml2_elevationtypeterm
				deferrable initially deferred
);

alter table gwml2_elevation owner to geonode;

create index if not exists gwml2_elevation_elevation_id
	on gwml2_elevation (elevation);

create index if not exists gwml2_elevation_elevation_accuracy_id_6afcf42d
	on gwml2_elevation (elevation_accuracy_id);

create index if not exists gwml2_elevation_elevation_measurement_method_id_f22b8f3a
	on gwml2_elevation (elevation_measurement_method_id);

create index if not exists gwml2_elevation_elevation_type_id_da9510a6
	on gwml2_elevation (elevation_type_id);

create table if not exists gwml2_bholestartpointtypeterm
(
	id serial not null
		constraint gwml2_bholestartpointtypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_bholestartpointtypeterm owner to geonode;

create table if not exists gwml2_boreholedrillingmethodterm
(
	id serial not null
		constraint gwml2_boreholedrillingmethodterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_boreholedrillingmethodterm owner to geonode;

create table if not exists gwml2_boreholeinclinationterm
(
	id serial not null
		constraint gwml2_boreholeinclinationterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_boreholeinclinationterm owner to geonode;

create table if not exists gwml2_ciaddress
(
	id serial not null
		constraint gwml2_ciaddress_pkey
			primary key,
	delivery_point text,
	city text,
	administrative_area text,
	postal_code text,
	country text,
	electronic_mail_address text
);

alter table gwml2_ciaddress owner to geonode;

create table if not exists gwml2_cionlinefunctionterm
(
	id serial not null
		constraint gwml2_cionlinefunctionterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_cionlinefunctionterm owner to geonode;

create table if not exists gwml2_ciroleterm
(
	id serial not null
		constraint gwml2_ciroleterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_ciroleterm owner to geonode;

create table if not exists gwml2_citelephone
(
	id serial not null
		constraint gwml2_citelephone_pkey
			primary key,
	voice text,
	facsimile text
);

alter table gwml2_citelephone owner to geonode;

create table if not exists gwml2_gmenvelope
(
	id serial not null
		constraint gwml2_gmenvelope_pkey
			primary key,
	upper_corner geometry(PointZ,4326),
	lower_corner geometry(PointZ,4326)
);

alter table gwml2_gmenvelope owner to geonode;

create index if not exists gwml2_gmenvelope_upper_corner_id
	on gwml2_gmenvelope (upper_corner);

create index if not exists gwml2_gmenvelope_lower_corner_id
	on gwml2_gmenvelope (lower_corner);

create table if not exists gwml2_cionlineresource
(
	id serial not null
		constraint gwml2_cionlineresource_pkey
			primary key,
	linkage text,
	protocol text,
	application_profile text,
	name text,
	description text
);

alter table gwml2_cionlineresource owner to geonode;

create table if not exists gwml2_cicontact
(
	id serial not null
		constraint gwml2_cicontact_pkey
			primary key,
	hours_of_service text,
	contact_instruction text,
	address_id integer
		constraint gwml2_cicontact_address_id_key
			unique
		constraint gwml2_cicontact_address_id_24a09fbe_fk_gwml2_ciaddress_id
			references gwml2_ciaddress
				deferrable initially deferred,
	online_resource_id integer
		constraint gwml2_cicontact_online_resource_id_key
			unique
		constraint gwml2_cicontact_online_resource_id_ed628bdd_fk_gwml2_cio
			references gwml2_cionlineresource
				deferrable initially deferred,
	phone_id integer
		constraint gwml2_cicontact_phone_id_key
			unique
		constraint gwml2_cicontact_phone_id_04713110_fk_gwml2_citelephone_id
			references gwml2_citelephone
				deferrable initially deferred
);

alter table gwml2_cicontact owner to geonode;

create table if not exists gwml2_ciresponsibleparty
(
	id serial not null
		constraint gwml2_ciresponsibleparty_pkey
			primary key,
	individual_name text,
	organisation_name text,
	position_name text,
	contact_info_id integer
		constraint gwml2_ciresponsibleparty_contact_info_id_key
			unique
		constraint gwml2_ciresponsiblep_contact_info_id_cdea57b0_fk_gwml2_cic
			references gwml2_cicontact
				deferrable initially deferred
);

alter table gwml2_ciresponsibleparty owner to geonode;

create table if not exists gwml2_borehole
(
	id serial not null
		constraint gwml2_borehole_pkey
			primary key,
	bhole_date_of_drilling date,
	bhole_nominal_diameter_id integer
		constraint gwml2_borehole_bhole_nominal_diameter_id_key
			unique
		constraint gwml2_borehole_bhole_nominal_diamet_6cb8bdb1_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	name text,
	bhole_core_interval_id integer
		constraint gwml2_borehole_bhole_core_interval__120bdc87_fk_gwml2_gme
			references gwml2_gmenvelope
				deferrable initially deferred,
	bhole_driller_id integer
		constraint gwml2_borehole_bhole_driller_id_ae6f1421_fk_gwml2_cir
			references gwml2_ciresponsibleparty
				deferrable initially deferred,
	bhole_inclination_type_id integer
		constraint gwml2_borehole_bhole_inclination_ty_02a9b191_fk_gwml2_bor
			references gwml2_boreholeinclinationterm
				deferrable initially deferred,
	bhole_operator_id integer
		constraint gwml2_borehole_bhole_operator_id_9ede8b50_fk_gwml2_cir
			references gwml2_ciresponsibleparty
				deferrable initially deferred,
	bhole_start_point_id integer
		constraint gwml2_borehole_bhole_start_point_id_6239a4a0_fk_gwml2_bho
			references gwml2_bholestartpointtypeterm
				deferrable initially deferred
);

alter table gwml2_borehole owner to geonode;

create index if not exists gwml2_borehole_bhole_core_interval_id_120bdc87
	on gwml2_borehole (bhole_core_interval_id);

create index if not exists gwml2_borehole_bhole_driller_id_ae6f1421
	on gwml2_borehole (bhole_driller_id);

create index if not exists gwml2_borehole_bhole_inclination_type_id_02a9b191
	on gwml2_borehole (bhole_inclination_type_id);

create index if not exists gwml2_borehole_bhole_operator_id_9ede8b50
	on gwml2_borehole (bhole_operator_id);

create index if not exists gwml2_borehole_bhole_start_point_id_6239a4a0
	on gwml2_borehole (bhole_start_point_id);

create table if not exists gwml2_ciresponsibleparty_role
(
	id serial not null
		constraint gwml2_ciresponsibleparty_role_pkey
			primary key,
	ciresponsibleparty_id integer not null
		constraint gwml2_ciresponsiblep_ciresponsibleparty_i_2fca3598_fk_gwml2_cir
			references gwml2_ciresponsibleparty
				deferrable initially deferred,
	ciroleterm_id integer not null
		constraint gwml2_ciresponsiblep_ciroleterm_id_d6b45f2d_fk_gwml2_cir
			references gwml2_ciroleterm
				deferrable initially deferred,
	constraint gwml2_ciresponsibleparty_ciresponsibleparty_id_ci_96f6ded4_uniq
		unique (ciresponsibleparty_id, ciroleterm_id)
);

alter table gwml2_ciresponsibleparty_role owner to geonode;

create index if not exists gwml2_ciresponsibleparty_role_ciresponsibleparty_id_2fca3598
	on gwml2_ciresponsibleparty_role (ciresponsibleparty_id);

create index if not exists gwml2_ciresponsibleparty_role_ciroleterm_id_d6b45f2d
	on gwml2_ciresponsibleparty_role (ciroleterm_id);

create table if not exists gwml2_cionlineresource_function
(
	id serial not null
		constraint gwml2_cionlineresource_function_pkey
			primary key,
	cionlineresource_id integer not null
		constraint gwml2_cionlineresour_cionlineresource_id_0be2eea6_fk_gwml2_cio
			references gwml2_cionlineresource
				deferrable initially deferred,
	cionlinefunctionterm_id integer not null
		constraint gwml2_cionlineresour_cionlinefunctionterm_3540acf9_fk_gwml2_cio
			references gwml2_cionlinefunctionterm
				deferrable initially deferred,
	constraint gwml2_cionlineresource_f_cionlineresource_id_cion_2d2c2c95_uniq
		unique (cionlineresource_id, cionlinefunctionterm_id)
);

alter table gwml2_cionlineresource_function owner to geonode;

create index if not exists gwml2_cionlineresource_function_cionlineresource_id_0be2eea6
	on gwml2_cionlineresource_function (cionlineresource_id);

create index if not exists gwml2_cionlineresource_fun_cionlinefunctionterm_id_3540acf9
	on gwml2_cionlineresource_function (cionlinefunctionterm_id);

create table if not exists gwml2_borehole_bhole_drilling_method
(
	id serial not null
		constraint gwml2_borehole_bhole_drilling_method_pkey
			primary key,
	borehole_id integer not null
		constraint gwml2_borehole_bhole_borehole_id_ea0960d1_fk_gwml2_bor
			references gwml2_borehole
				deferrable initially deferred,
	boreholedrillingmethodterm_id integer not null
		constraint gwml2_borehole_bhole_boreholedrillingmeth_f72e66fc_fk_gwml2_bor
			references gwml2_boreholedrillingmethodterm
				deferrable initially deferred,
	constraint gwml2_borehole_bhole_dri_borehole_id_boreholedril_2bae1790_uniq
		unique (borehole_id, boreholedrillingmethodterm_id)
);

alter table gwml2_borehole_bhole_drilling_method owner to geonode;

create index if not exists gwml2_borehole_bhole_drilling_method_borehole_id_ea0960d1
	on gwml2_borehole_bhole_drilling_method (borehole_id);

create index if not exists gwml2_borehole_bhole_drill_boreholedrillingmethodterm_f72e66fc
	on gwml2_borehole_bhole_drilling_method (boreholedrillingmethodterm_id);

create table if not exists gwml2_borehole_bhole_material_custodian
(
	id serial not null
		constraint gwml2_borehole_bhole_material_custodian_pkey
			primary key,
	borehole_id integer not null
		constraint gwml2_borehole_bhole_borehole_id_b45bf3b8_fk_gwml2_bor
			references gwml2_borehole
				deferrable initially deferred,
	ciresponsibleparty_id integer not null
		constraint gwml2_borehole_bhole_ciresponsibleparty_i_a3590505_fk_gwml2_cir
			references gwml2_ciresponsibleparty
				deferrable initially deferred,
	constraint gwml2_borehole_bhole_mat_borehole_id_ciresponsibl_2876dde8_uniq
		unique (borehole_id, ciresponsibleparty_id)
);

alter table gwml2_borehole_bhole_material_custodian owner to geonode;

create index if not exists gwml2_borehole_bhole_material_custodian_borehole_id_b45bf3b8
	on gwml2_borehole_bhole_material_custodian (borehole_id);

create index if not exists gwml2_borehole_bhole_mater_ciresponsibleparty_id_a3590505
	on gwml2_borehole_bhole_material_custodian (ciresponsibleparty_id);

create table if not exists gwml2_equipmenttypeterm
(
	id serial not null
		constraint gwml2_equipmenttypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_equipmenttypeterm owner to geonode;

create table if not exists gwml2_equipment
(
	id serial not null
		constraint gwml2_equipment_pkey
			primary key,
	installation_date date,
	equipment_type_id integer
		constraint gwml2_equipment_equipment_type_id_a5753cc7_fk_gwml2_equ
			references gwml2_equipmenttypeterm
				deferrable initially deferred
);

alter table gwml2_equipment owner to geonode;

create index if not exists gwml2_equipment_equipment_type_id_a5753cc7
	on gwml2_equipment (equipment_type_id);

create table if not exists gwml2_equipment_characteristics
(
	id serial not null
		constraint gwml2_equipment_characteristics_pkey
			primary key,
	equipment_id integer not null
		constraint gwml2_equipment_char_equipment_id_b59efea1_fk_gwml2_equ
			references gwml2_equipment
				deferrable initially deferred,
	namedvalue_id integer not null,
	constraint gwml2_equipment_characte_equipment_id_equipmentch_7500eb26_uniq
		unique (equipment_id, namedvalue_id)
);

alter table gwml2_equipment_characteristics owner to geonode;

create index if not exists gwml2_equipment_characteristics_equipment_id_b59efea1
	on gwml2_equipment_characteristics (equipment_id);

create index if not exists gwml2_equipment_characteri_equipmentcharacteristicter_dce694cc
	on gwml2_equipment_characteristics (namedvalue_id);

create table if not exists gwml2_borehole_installed_equipment
(
	id serial not null
		constraint gwml2_borehole_installed_equipment_pkey
			primary key,
	borehole_id integer not null
		constraint gwml2_borehole_insta_borehole_id_e1749a50_fk_gwml2_bor
			references gwml2_borehole
				deferrable initially deferred,
	equipment_id integer not null
		constraint gwml2_borehole_insta_equipment_id_693bbd46_fk_gwml2_equ
			references gwml2_equipment
				deferrable initially deferred,
	constraint gwml2_borehole_installed_borehole_id_equipment_id_b08fcd9a_uniq
		unique (borehole_id, equipment_id)
);

alter table gwml2_borehole_installed_equipment owner to geonode;

create index if not exists gwml2_borehole_installed_equipment_borehole_id_e1749a50
	on gwml2_borehole_installed_equipment (borehole_id);

create index if not exists gwml2_borehole_installed_equipment_equipment_id_693bbd46
	on gwml2_borehole_installed_equipment (equipment_id);

create table if not exists gwml2_namedvalue
(
	id serial not null
		constraint gwml2_namedvalue_pkey
			primary key,
	name text,
	value text
);

alter table gwml2_namedvalue owner to geonode;

create table if not exists gwml2_tmperiod
(
	id serial not null
		constraint gwml2_tmperiod_pkey
			primary key,
	start_time timestamp with time zone,
	end_time timestamp with time zone
);

alter table gwml2_tmperiod owner to geonode;

create table if not exists gwml2_omobservation
(
	id serial not null
		constraint gwml2_omobservation_pkey
			primary key,
	phenomenon_time timestamp with time zone,
	result_time timestamp with time zone,
	"resultQuality" text,
	valid_time_id integer
		constraint gwml2_omobservation_valid_time_id_c6b6d184_fk_gwml2_tmperiod_id
			references gwml2_tmperiod
				deferrable initially deferred
);

alter table gwml2_omobservation owner to geonode;

create index if not exists gwml2_omobservation_valid_time_id_c6b6d184
	on gwml2_omobservation (valid_time_id);

create table if not exists gwml2_omobservation_parameter
(
	id serial not null
		constraint gwml2_omobservation_parameter_pkey
			primary key,
	omobservation_id integer not null
		constraint gwml2_omobservation__omobservation_id_25ff6f27_fk_gwml2_omo
			references gwml2_omobservation
				deferrable initially deferred,
	namedvalue_id integer not null
		constraint gwml2_omobservation__namedvalue_id_eb77f766_fk_gwml2_nam
			references gwml2_namedvalue
				deferrable initially deferred,
	constraint gwml2_omobservation_para_omobservation_id_namedva_cce367eb_uniq
		unique (omobservation_id, namedvalue_id)
);

alter table gwml2_omobservation_parameter owner to geonode;

create index if not exists gwml2_omobservation_parameter_omobservation_id_25ff6f27
	on gwml2_omobservation_parameter (omobservation_id);

create index if not exists gwml2_omobservation_parameter_namedvalue_id_eb77f766
	on gwml2_omobservation_parameter (namedvalue_id);

create table if not exists gwml2_gwstringtype
(
	id serial not null
		constraint gwml2_gwstringtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_gwstringtype owner to geonode;

create table if not exists gwml2_springcausetype
(
	id serial not null
		constraint gwml2_springcausetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_springcausetype owner to geonode;

create table if not exists gwml2_springpersistencetype
(
	id serial not null
		constraint gwml2_springpersistencetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_springpersistencetype owner to geonode;

create table if not exists gwml2_gwspring
(
	id serial not null
		constraint gwml2_gwspring_pkey
			primary key,
	gw_spring_name text not null,
	gw_spring_location geometry(Geometry,4326),
	gw_spring_construction text,
	"gwSpringPersistence_id" integer
		constraint "gwml2_gwspring_gwSpringPersistence__cdf8c7f3_fk_gwml2_spr"
			references gwml2_springpersistencetype
				deferrable initially deferred,
	gw_spring_cause_type_id integer
		constraint gwml2_gwspring_gw_spring_cause_type_0ad50648_fk_gwml2_spr
			references gwml2_springcausetype
				deferrable initially deferred,
	gw_spring_type_id integer
		constraint gwml2_gwspring_gw_spring_type_id_04e4abd8_fk_gwml2_gws
			references gwml2_gwstringtype
				deferrable initially deferred
);

alter table gwml2_gwspring owner to geonode;

create index if not exists gwml2_gwspring_gw_spring_location_id
	on gwml2_gwspring (gw_spring_location);

create index if not exists "gwml2_gwspring_gwSpringPersistence_id_cdf8c7f3"
	on gwml2_gwspring ("gwSpringPersistence_id");

create index if not exists gwml2_gwspring_gw_spring_cause_type_id_0ad50648
	on gwml2_gwspring (gw_spring_cause_type_id);

create index if not exists gwml2_gwspring_gw_spring_type_id_04e4abd8
	on gwml2_gwspring (gw_spring_type_id);

create table if not exists gwml2_gwspring_gw_spring_body
(
	id serial not null
		constraint gwml2_gwspring_gw_spring_body_pkey
			primary key,
	gwspring_id integer not null
		constraint gwml2_gwspring_gw_sp_gwspring_id_e85ffa39_fk_gwml2_gws
			references gwml2_gwspring
				deferrable initially deferred,
	gwfluidbody_id integer not null
		constraint gwml2_gwspring_gw_sp_gwfluidbody_id_1721fdb5_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	constraint gwml2_gwspring_gw_spring_gwspring_id_gwfluidbody__b6461a1e_uniq
		unique (gwspring_id, gwfluidbody_id)
);

alter table gwml2_gwspring_gw_spring_body owner to geonode;

create index if not exists gwml2_gwspring_gw_spring_body_gwspring_id_e85ffa39
	on gwml2_gwspring_gw_spring_body (gwspring_id);

create index if not exists gwml2_gwspring_gw_spring_body_gwfluidbody_id_1721fdb5
	on gwml2_gwspring_gw_spring_body (gwfluidbody_id);

create table if not exists gwml2_gwspring_gw_spring_licence
(
	id serial not null
		constraint gwml2_gwspring_gw_spring_licence_pkey
			primary key,
	gwspring_id integer not null
		constraint gwml2_gwspring_gw_sp_gwspring_id_7d8ee98a_fk_gwml2_gws
			references gwml2_gwspring
				deferrable initially deferred,
	gwlicence_id integer not null
		constraint gwml2_gwspring_gw_sp_gwlicence_id_8058d91a_fk_gwml2_gwl
			references gwml2_gwlicence
				deferrable initially deferred,
	constraint gwml2_gwspring_gw_spring_gwspring_id_gwlicence_id_c0639961_uniq
		unique (gwspring_id, gwlicence_id)
);

alter table gwml2_gwspring_gw_spring_licence owner to geonode;

create index if not exists gwml2_gwspring_gw_spring_licence_gwspring_id_7d8ee98a
	on gwml2_gwspring_gw_spring_licence (gwspring_id);

create index if not exists gwml2_gwspring_gw_spring_licence_gwlicence_id_8058d91a
	on gwml2_gwspring_gw_spring_licence (gwlicence_id);

create table if not exists gwml2_gwspring_gw_spring_reference_elevation
(
	id serial not null
		constraint gwml2_gwspring_gw_spring_reference_elevation_pkey
			primary key,
	gwspring_id integer not null
		constraint gwml2_gwspring_gw_sp_gwspring_id_89211aa0_fk_gwml2_gws
			references gwml2_gwspring
				deferrable initially deferred,
	elevation_id integer not null
		constraint gwml2_gwspring_gw_sp_elevation_id_9167c606_fk_gwml2_ele
			references gwml2_elevation
				deferrable initially deferred,
	constraint gwml2_gwspring_gw_spring_gwspring_id_elevation_id_f2f5823a_uniq
		unique (gwspring_id, elevation_id)
);

alter table gwml2_gwspring_gw_spring_reference_elevation owner to geonode;

create index if not exists gwml2_gwspring_gw_spring_r_gwspring_id_89211aa0
	on gwml2_gwspring_gw_spring_reference_elevation (gwspring_id);

create index if not exists gwml2_gwspring_gw_spring_r_elevation_id_9167c606
	on gwml2_gwspring_gw_spring_reference_elevation (elevation_id);

create table if not exists gwml2_flowpersistencetype
(
	id serial not null
		constraint gwml2_flowpersistencetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_flowpersistencetype owner to geonode;

create table if not exists gwml2_gwdischarge
(
	id serial not null
		constraint gwml2_gwdischarge_pkey
			primary key,
	flow_rate_id integer not null
		constraint gwml2_gwdischarge_flow_rate_id_89846767_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_gwdischarge owner to geonode;

create index if not exists gwml2_gwdischarge_flow_rate_id_89846767
	on gwml2_gwdischarge (flow_rate_id);

create table if not exists gwml2_gwintraflow
(
	id serial not null
		constraint gwml2_gwintraflow_pkey
			primary key,
	gw_flow_location geometry(MultiPoint,4326) not null
);

alter table gwml2_gwintraflow owner to geonode;

create index if not exists gwml2_gwintraflow_gw_flow_location_id
	on gwml2_gwintraflow (gw_flow_location);

create table if not exists gwml2_waterflowprocess
(
	id serial not null
		constraint gwml2_waterflowprocess_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_waterflowprocess owner to geonode;

create table if not exists gwml2_gwrecharge
(
	id serial not null
		constraint gwml2_gwrecharge_pkey
			primary key,
	flow_rate_id integer not null
		constraint gwml2_gwrecharge_flow_rate_id_49adeef2_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_gwrecharge owner to geonode;

create index if not exists gwml2_gwrecharge_flow_rate_id_49adeef2
	on gwml2_gwrecharge (flow_rate_id);

create table if not exists gwml2_gwinterflow
(
	id serial not null
		constraint gwml2_gwinterflow_pkey
			primary key,
	gw_flow_location geometry(MultiPoint,4326) not null
);

alter table gwml2_gwinterflow owner to geonode;

create index if not exists gwml2_gwinterflow_gw_flow_location_id
	on gwml2_gwinterflow (gw_flow_location);

create table if not exists gwml2_gwinterflow_gw_discharge
(
	id serial not null
		constraint gwml2_gwinterflow_gw_discharge_pkey
			primary key,
	gwinterflow_id integer not null
		constraint gwml2_gwinterflow_gw_gwinterflow_id_f0fdd0a8_fk_gwml2_gwi
			references gwml2_gwinterflow
				deferrable initially deferred,
	gwdischarge_id integer not null
		constraint gwml2_gwinterflow_gw_gwdischarge_id_0a94564d_fk_gwml2_gwd
			references gwml2_gwdischarge
				deferrable initially deferred,
	constraint gwml2_gwinterflow_gw_dis_gwinterflow_id_gwdischar_a1100bcf_uniq
		unique (gwinterflow_id, gwdischarge_id)
);

alter table gwml2_gwinterflow_gw_discharge owner to geonode;

create index if not exists gwml2_gwinterflow_gw_discharge_gwinterflow_id_f0fdd0a8
	on gwml2_gwinterflow_gw_discharge (gwinterflow_id);

create index if not exists gwml2_gwinterflow_gw_discharge_gwdischarge_id_0a94564d
	on gwml2_gwinterflow_gw_discharge (gwdischarge_id);

create table if not exists gwml2_gwinterflow_gw_recharge
(
	id serial not null
		constraint gwml2_gwinterflow_gw_recharge_pkey
			primary key,
	gwinterflow_id integer not null
		constraint gwml2_gwinterflow_gw_gwinterflow_id_6bad0ee7_fk_gwml2_gwi
			references gwml2_gwinterflow
				deferrable initially deferred,
	gwrecharge_id integer not null
		constraint gwml2_gwinterflow_gw_gwrecharge_id_866b47ad_fk_gwml2_gwr
			references gwml2_gwrecharge
				deferrable initially deferred,
	constraint gwml2_gwinterflow_gw_rec_gwinterflow_id_gwrecharg_1faf8c42_uniq
		unique (gwinterflow_id, gwrecharge_id)
);

alter table gwml2_gwinterflow_gw_recharge owner to geonode;

create index if not exists gwml2_gwinterflow_gw_recharge_gwinterflow_id_6bad0ee7
	on gwml2_gwinterflow_gw_recharge (gwinterflow_id);

create index if not exists gwml2_gwinterflow_gw_recharge_gwrecharge_id_866b47ad
	on gwml2_gwinterflow_gw_recharge (gwrecharge_id);

create table if not exists gwml2_gwflowsystem
(
	id serial not null
		constraint gwml2_gwflowsystem_pkey
			primary key,
	gw_flow_path geometry(Geometry,4326) not null,
	gw_part_of_system_flow_id integer
		constraint gwml2_gwflowsystem_gw_part_of_system_fl_9b18dbc3_fk_gwml2_gwf
			references gwml2_gwflowsystem
				deferrable initially deferred
);

alter table gwml2_gwflowsystem owner to geonode;

create index if not exists gwml2_gwflowsystem_gw_flow_path_id
	on gwml2_gwflowsystem (gw_flow_path);

create index if not exists gwml2_gwflowsystem_gw_part_of_system_flow_id_9b18dbc3
	on gwml2_gwflowsystem (gw_part_of_system_flow_id);

create table if not exists gwml2_aquifertypeterm
(
	id serial not null
		constraint gwml2_aquifertypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_aquifertypeterm owner to geonode;

create table if not exists gwml2_conductivityconfinementtypeterm
(
	id serial not null
		constraint gwml2_conductivityconfinementtypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_conductivityconfinementtypeterm owner to geonode;

create table if not exists gwml2_gwaquifer
(
	id serial not null
		constraint gwml2_gwaquifer_pkey
			primary key,
	gw_aquifer_is_exploited boolean,
	gw_aquifer_is_main boolean,
	gw_aquifer_type_id integer
		constraint gwml2_gwaquifer_gw_aquifer_type_id_40fbde8e_fk_gwml2_aqu
			references gwml2_aquifertypeterm
				deferrable initially deferred
);

alter table gwml2_gwaquifer owner to geonode;

create index if not exists gwml2_gwaquifer_gw_aquifer_type_id_40fbde8e
	on gwml2_gwaquifer (gw_aquifer_type_id);

create table if not exists gwml2_gwaquifersystem
(
	id serial not null
		constraint gwml2_gwaquifersystem_pkey
			primary key,
	gw_aquifer_system_is_layered boolean
);

alter table gwml2_gwaquifersystem owner to geonode;

create table if not exists gwml2_porositytypeterm
(
	id serial not null
		constraint gwml2_porositytypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_porositytypeterm owner to geonode;

create table if not exists gwml2_spatialconfinementtypeterm
(
	id serial not null
		constraint gwml2_spatialconfinementtypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_spatialconfinementtypeterm owner to geonode;

create table if not exists gwml2_unitpropertyterm
(
	id serial not null
		constraint gwml2_unitpropertyterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_unitpropertyterm owner to geonode;

create table if not exists gwml2_gwunitproperties
(
	id serial not null
		constraint gwml2_gwunitproperties_pkey
			primary key,
	gw_unit_property_value text not null,
	gw_unit_property_id integer not null
		constraint gwml2_gwunitproperti_gw_unit_property_id_4abdcdde_fk_gwml2_uni
			references gwml2_unitpropertyterm
				deferrable initially deferred
);

alter table gwml2_gwunitproperties owner to geonode;

create index if not exists gwml2_gwunitproperties_gw_unit_property_id_4abdcdde
	on gwml2_gwunitproperties (gw_unit_property_id);

create table if not exists gwml2_gwporosity
(
	id serial not null
		constraint gwml2_gwporosity_pkey
			primary key,
	gw_porosity_id integer
		constraint gwml2_gwporosity_gw_porosity_id_0c1b8bb1_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	gw_porosity_type_id integer
		constraint gwml2_gwporosity_gw_porosity_type_id_b7a1acd6_fk_gwml2_por
			references gwml2_porositytypeterm
				deferrable initially deferred
);

alter table gwml2_gwporosity owner to geonode;

create index if not exists gwml2_gwporosity_gw_porosity_id_0c1b8bb1
	on gwml2_gwporosity (gw_porosity_id);

create index if not exists gwml2_gwporosity_gw_porosity_type_id_b7a1acd6
	on gwml2_gwporosity (gw_porosity_type_id);

create table if not exists gwml2_gwdivide
(
	id serial not null
		constraint gwml2_gwdivide_pkey
			primary key,
	gw_divide_shape geometry(Geometry,4326) not null
);

alter table gwml2_gwdivide owner to geonode;

create index if not exists gwml2_gwdivide_gw_divide_shape_id
	on gwml2_gwdivide (gw_divide_shape);

create table if not exists gwml2_gwdivide_gw_flow_system
(
	id serial not null
		constraint gwml2_gwdivide_gw_flow_system_pkey
			primary key,
	gwdivide_id integer not null
		constraint gwml2_gwdivide_gw_fl_gwdivide_id_770571ad_fk_gwml2_gwd
			references gwml2_gwdivide
				deferrable initially deferred,
	gwflowsystem_id integer not null
		constraint gwml2_gwdivide_gw_fl_gwflowsystem_id_0d7ddf2d_fk_gwml2_gwf
			references gwml2_gwflowsystem
				deferrable initially deferred,
	constraint gwml2_gwdivide_gw_flow_s_gwdivide_id_gwflowsystem_c70fc496_uniq
		unique (gwdivide_id, gwflowsystem_id)
);

alter table gwml2_gwdivide_gw_flow_system owner to geonode;

create index if not exists gwml2_gwdivide_gw_flow_system_gwdivide_id_770571ad
	on gwml2_gwdivide_gw_flow_system (gwdivide_id);

create index if not exists gwml2_gwdivide_gw_flow_system_gwflowsystem_id_0d7ddf2d
	on gwml2_gwdivide_gw_flow_system (gwflowsystem_id);

create table if not exists gwml2_gwconfiningbed
(
	id serial not null
		constraint gwml2_gwconfiningbed_pkey
			primary key,
	gw_conductivity_confinement_id integer
		constraint gwml2_gwconfiningbed_gw_conductivity_conf_1971b1ac_fk_gwml2_con
			references gwml2_conductivityconfinementtypeterm
				deferrable initially deferred,
	gw_spatial_confinement_id integer
		constraint gwml2_gwconfiningbed_gw_spatial_confineme_9562e935_fk_gwml2_spa
			references gwml2_spatialconfinementtypeterm
				deferrable initially deferred
);

alter table gwml2_gwconfiningbed owner to geonode;

create index if not exists gwml2_gwconfiningbed_gw_conductivity_confinement_id_1971b1ac
	on gwml2_gwconfiningbed (gw_conductivity_confinement_id);

create index if not exists gwml2_gwconfiningbed_gw_spatial_confinement_id_9562e935
	on gwml2_gwconfiningbed (gw_spatial_confinement_id);

create table if not exists gwml2_gwbasin
(
	id serial not null
		constraint gwml2_gwbasin_pkey
			primary key
);

alter table gwml2_gwbasin owner to geonode;

create table if not exists gwml2_gwbasin_gw_divide
(
	id serial not null
		constraint gwml2_gwbasin_gw_divide_pkey
			primary key,
	gwbasin_id integer not null
		constraint gwml2_gwbasin_gw_divide_gwbasin_id_9d3c65c1_fk_gwml2_gwbasin_id
			references gwml2_gwbasin
				deferrable initially deferred,
	gwdivide_id integer not null
		constraint gwml2_gwbasin_gw_div_gwdivide_id_f1ed0d6b_fk_gwml2_gwd
			references gwml2_gwdivide
				deferrable initially deferred,
	constraint gwml2_gwbasin_gw_divide_gwbasin_id_gwdivide_id_0399cc9e_uniq
		unique (gwbasin_id, gwdivide_id)
);

alter table gwml2_gwbasin_gw_divide owner to geonode;

create index if not exists gwml2_gwbasin_gw_divide_gwbasin_id_9d3c65c1
	on gwml2_gwbasin_gw_divide (gwbasin_id);

create index if not exists gwml2_gwbasin_gw_divide_gwdivide_id_f1ed0d6b
	on gwml2_gwbasin_gw_divide (gwdivide_id);

create table if not exists gwml2_gwaquiferunit
(
	id serial not null
		constraint gwml2_gwaquiferunit_pkey
			primary key,
	gw_aquifer_id integer
		constraint gwml2_gwaquiferunit_gw_aquifer_id_dca7863b_fk_gwml2_gwa
			references gwml2_gwaquifer
				deferrable initially deferred,
	gw_confining_bed_id integer
		constraint gwml2_gwaquiferunit_gw_confining_bed_id_207cd194_fk_gwml2_gwc
			references gwml2_gwconfiningbed
				deferrable initially deferred
);

alter table gwml2_gwaquiferunit owner to geonode;

create index if not exists gwml2_gwaquiferunit_gw_aquifer_id_dca7863b
	on gwml2_gwaquiferunit (gw_aquifer_id);

create index if not exists gwml2_gwaquiferunit_gw_confining_bed_id_207cd194
	on gwml2_gwaquiferunit (gw_confining_bed_id);

create table if not exists gwml2_gwaquiferunit_gw_aquifer_system
(
	id serial not null
		constraint gwml2_gwaquiferunit_gw_aquifer_system_pkey
			primary key,
	gwaquiferunit_id integer not null
		constraint gwml2_gwaquiferunit__gwaquiferunit_id_a5cd8612_fk_gwml2_gwa
			references gwml2_gwaquiferunit
				deferrable initially deferred,
	gwaquifersystem_id integer not null
		constraint gwml2_gwaquiferunit__gwaquifersystem_id_6a128c1f_fk_gwml2_gwa
			references gwml2_gwaquifersystem
				deferrable initially deferred,
	constraint gwml2_gwaquiferunit_gw_a_gwaquiferunit_id_gwaquif_f26e5ebd_uniq
		unique (gwaquiferunit_id, gwaquifersystem_id)
);

alter table gwml2_gwaquiferunit_gw_aquifer_system owner to geonode;

create index if not exists gwml2_gwaquiferunit_gw_aquifer_system_gwaquiferunit_id_a5cd8612
	on gwml2_gwaquiferunit_gw_aquifer_system (gwaquiferunit_id);

create index if not exists gwml2_gwaquiferunit_gw_aqu_gwaquifersystem_id_6a128c1f
	on gwml2_gwaquiferunit_gw_aquifer_system (gwaquifersystem_id);

create table if not exists gwml2_gwaquifer_gw_confining_bed
(
	id serial not null
		constraint gwml2_gwaquifer_gw_confining_bed_pkey
			primary key,
	gwaquifer_id integer not null
		constraint gwml2_gwaquifer_gw_c_gwaquifer_id_b0840951_fk_gwml2_gwa
			references gwml2_gwaquifer
				deferrable initially deferred,
	gwconfiningbed_id integer not null
		constraint gwml2_gwaquifer_gw_c_gwconfiningbed_id_b6f60af7_fk_gwml2_gwc
			references gwml2_gwconfiningbed
				deferrable initially deferred,
	constraint gwml2_gwaquifer_gw_confi_gwaquifer_id_gwconfining_c379103b_uniq
		unique (gwaquifer_id, gwconfiningbed_id)
);

alter table gwml2_gwaquifer_gw_confining_bed owner to geonode;

create index if not exists gwml2_gwaquifer_gw_confining_bed_gwaquifer_id_b0840951
	on gwml2_gwaquifer_gw_confining_bed (gwaquifer_id);

create index if not exists gwml2_gwaquifer_gw_confining_bed_gwconfiningbed_id_b6f60af7
	on gwml2_gwaquifer_gw_confining_bed (gwconfiningbed_id);

create table if not exists gwml2_chemicaltype
(
	id serial not null
		constraint gwml2_chemicaltype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_chemicaltype owner to geonode;

create table if not exists gwml2_constituentrelationtype
(
	id serial not null
		constraint gwml2_constituentrelationtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_constituentrelationtype owner to geonode;

create table if not exists gwml2_gwbodypropertytype
(
	id serial not null
		constraint gwml2_gwbodypropertytype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_gwbodypropertytype owner to geonode;

create table if not exists gwml2_gwchemicalconstituent
(
	id serial not null
		constraint gwml2_gwchemicalconstituent_pkey
			primary key,
	gw_chemical_id integer
		constraint gwml2_gwchemicalcons_gw_chemical_id_d63e8dcc_fk_gwml2_che
			references gwml2_chemicaltype
				deferrable initially deferred
);

alter table gwml2_gwchemicalconstituent owner to geonode;

create index if not exists gwml2_gwchemicalconstituent_gw_chemical_id_d63e8dcc
	on gwml2_gwchemicalconstituent (gw_chemical_id);

create table if not exists gwml2_materialtype
(
	id serial not null
		constraint gwml2_materialtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_materialtype owner to geonode;

create table if not exists gwml2_mechanismtype
(
	id serial not null
		constraint gwml2_mechanismtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_mechanismtype owner to geonode;

create table if not exists gwml2_mixturetype
(
	id serial not null
		constraint gwml2_mixturetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_mixturetype owner to geonode;

create table if not exists gwml2_gwmixture
(
	id serial not null
		constraint gwml2_gwmixture_pkey
			primary key,
	gw_mixture_id integer not null
		constraint gwml2_gwmixture_gw_mixture_id_d59160f2_fk_gwml2_mixturetype_id
			references gwml2_mixturetype
				deferrable initially deferred
);

alter table gwml2_gwmixture owner to geonode;

create index if not exists gwml2_gwmixture_gw_mixture_id_d59160f2
	on gwml2_gwmixture (gw_mixture_id);

create table if not exists gwml2_organismtype
(
	id serial not null
		constraint gwml2_organismtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_organismtype owner to geonode;

create table if not exists gwml2_statetype
(
	id serial not null
		constraint gwml2_statetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_statetype owner to geonode;

create table if not exists gwml2_gwbiologicconstituent
(
	id serial not null
		constraint gwml2_gwbiologicconstituent_pkey
			primary key,
	gw_organism_id integer
		constraint gwml2_gwbiologiccons_gw_organism_id_ff07d502_fk_gwml2_org
			references gwml2_organismtype
				deferrable initially deferred,
	gw_state_id integer
		constraint gwml2_gwbiologiccons_gw_state_id_fe985ea3_fk_gwml2_sta
			references gwml2_statetype
				deferrable initially deferred
);

alter table gwml2_gwbiologicconstituent owner to geonode;

create index if not exists gwml2_gwbiologicconstituent_gw_organism_id_ff07d502
	on gwml2_gwbiologicconstituent (gw_organism_id);

create index if not exists gwml2_gwbiologicconstituent_gw_state_id_fe985ea3
	on gwml2_gwbiologicconstituent (gw_state_id);

create table if not exists gwml2_surfacetype
(
	id serial not null
		constraint gwml2_surfacetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_surfacetype owner to geonode;

create table if not exists gwml2_gwmaterialconstituent
(
	id serial not null
		constraint gwml2_gwmaterialconstituent_pkey
			primary key,
	gw_material_id integer
		constraint gwml2_gwmaterialcons_gw_material_id_d72f2192_fk_gwml2_mat
			references gwml2_materialtype
				deferrable initially deferred
);

alter table gwml2_gwmaterialconstituent owner to geonode;

create table if not exists gwml2_gwconstituent
(
	id serial not null
		constraint gwml2_gwconstituent_pkey
			primary key,
	gw_biologic_constituent_id integer
		constraint gwml2_gwconstituent_gw_biologic_constitu_fc11c9fb_fk_gwml2_gwb
			references gwml2_gwbiologicconstituent
				deferrable initially deferred,
	gw_chemical_constituent_id integer
		constraint gwml2_gwconstituent_gw_chemical_constitu_75c90de2_fk_gwml2_gwc
			references gwml2_gwchemicalconstituent
				deferrable initially deferred,
	gw_concentration_id integer
		constraint gwml2_gwconstituent_gw_concentration_id_key
			unique
		constraint gwml2_gwconstituent_gw_concentration_id_750811ef_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_material_constituent_id integer
		constraint gwml2_gwconstituent_gw_material_constitu_100a3289_fk_gwml2_gwm
			references gwml2_gwmaterialconstituent
				deferrable initially deferred,
	gw_state_id integer
		constraint gwml2_gwconstituent_gw_state_id_a917cad7_fk_gwml2_statetype_id
			references gwml2_statetype
				deferrable initially deferred,
	gw_constitute_of_id integer
);

alter table gwml2_gwconstituent owner to geonode;

create index if not exists gwml2_gwconstituent_gw_biologic_constituent_id_fc11c9fb
	on gwml2_gwconstituent (gw_biologic_constituent_id);

create index if not exists gwml2_gwconstituent_gw_chemical_constituent_id_75c90de2
	on gwml2_gwconstituent (gw_chemical_constituent_id);

create index if not exists gwml2_gwconstituent_gw_material_constituent_id_100a3289
	on gwml2_gwconstituent (gw_material_constituent_id);

create index if not exists gwml2_gwconstituent_gw_state_id_a917cad7
	on gwml2_gwconstituent (gw_state_id);

create index if not exists gwml2_gwconstituent_gw_constitute_of_id_bda33346
	on gwml2_gwconstituent (gw_constitute_of_id);

create table if not exists gwml2_gwmixtureconstituent
(
	id serial not null
		constraint gwml2_gwmixtureconstituent_pkey
			primary key,
	gw_constituent_id integer not null
		constraint gwml2_gwmixtureconst_gw_constituent_id_986fbe62_fk_gwml2_gwc
			references gwml2_gwconstituent
				deferrable initially deferred,
	gw_mixture_id integer not null
		constraint gwml2_gwmixtureconst_gw_mixture_id_0db5405f_fk_gwml2_gwm
			references gwml2_gwmixture
				deferrable initially deferred
);

alter table gwml2_gwmixtureconstituent owner to geonode;

create index if not exists gwml2_gwmixtureconstituent_gw_constituent_id_986fbe62
	on gwml2_gwmixtureconstituent (gw_constituent_id);

create index if not exists gwml2_gwmixtureconstituent_gw_mixture_id_0db5405f
	on gwml2_gwmixtureconstituent (gw_mixture_id);

create index if not exists gwml2_gwmaterialconstituent_gw_material_id_d72f2192
	on gwml2_gwmaterialconstituent (gw_material_id);

create table if not exists gwml2_gwfluidbodysurface
(
	id serial not null
		constraint gwml2_gwfluidbodysurface_pkey
			primary key,
	gw_surface_shape geometry(Geometry,4326),
	gw_surface_metadata_id integer
		constraint gwml2_gwfluidbodysur_gw_surface_metadata__c8bbeda7_fk_gwml2_omo
			references gwml2_omobservation
				deferrable initially deferred,
	gw_surface_type_id integer
		constraint gwml2_gwfluidbodysur_gw_surface_type_id_1279f8c7_fk_gwml2_sur
			references gwml2_surfacetype
				deferrable initially deferred
);

alter table gwml2_gwfluidbodysurface owner to geonode;

create index if not exists gwml2_gwfluidbodysurface_gw_surface_shape_id
	on gwml2_gwfluidbodysurface (gw_surface_shape);

create index if not exists gwml2_gwfluidbodysurface_gw_surface_metadata_id_c8bbeda7
	on gwml2_gwfluidbodysurface (gw_surface_metadata_id);

create index if not exists gwml2_gwfluidbodysurface_gw_surface_type_id_1279f8c7
	on gwml2_gwfluidbodysurface (gw_surface_type_id);

create table if not exists gwml2_gwfluidbodysurface_gw_surface_divide
(
	id serial not null
		constraint gwml2_gwfluidbodysurface_gw_surface_divide_pkey
			primary key,
	gwfluidbodysurface_id integer not null
		constraint gwml2_gwfluidbodysur_gwfluidbodysurface_i_378f75f4_fk_gwml2_gwf
			references gwml2_gwfluidbodysurface
				deferrable initially deferred,
	gwdivide_id integer not null
		constraint gwml2_gwfluidbodysur_gwdivide_id_7816fafa_fk_gwml2_gwd
			references gwml2_gwdivide
				deferrable initially deferred,
	constraint gwml2_gwfluidbodysurface_gwfluidbodysurface_id_gw_f65db8fe_uniq
		unique (gwfluidbodysurface_id, gwdivide_id)
);

alter table gwml2_gwfluidbodysurface_gw_surface_divide owner to geonode;

create index if not exists gwml2_gwfluidbodysurface_g_gwfluidbodysurface_id_378f75f4
	on gwml2_gwfluidbodysurface_gw_surface_divide (gwfluidbodysurface_id);

create index if not exists gwml2_gwfluidbodysurface_gw_surface_divide_gwdivide_id_7816fafa
	on gwml2_gwfluidbodysurface_gw_surface_divide (gwdivide_id);

create table if not exists gwml2_gwfluidbodyproperty
(
	id serial not null
		constraint gwml2_gwfluidbodyproperty_pkey
			primary key,
	gw_body_property_id integer
		constraint gwml2_gwfluidbodypro_gw_body_property_id_49f5aa3a_fk_gwml2_gwb
			references gwml2_gwbodypropertytype
				deferrable initially deferred,
	gw_body_property_value_id integer
		constraint gwml2_gwfluidbodypro_gw_body_property_val_8264319e_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_gwfluidbodyproperty owner to geonode;

create index if not exists gwml2_gwfluidbodyproperty_gw_body_property_id_49f5aa3a
	on gwml2_gwfluidbodyproperty (gw_body_property_id);

create index if not exists gwml2_gwfluidbodyproperty_gw_body_property_value_id_8264319e
	on gwml2_gwfluidbodyproperty (gw_body_property_value_id);

create table if not exists gwml2_gwconstituentrelation
(
	id serial not null
		constraint gwml2_gwconstituentrelation_pkey
			primary key,
	gw_constituent_relation_type_id integer
		constraint gwml2_gwconstituentr_gw_constituent_relat_841bd855_fk_gwml2_con
			references gwml2_constituentrelationtype
				deferrable initially deferred,
	gw_constitution_relation_mechanism_id integer
		constraint gwml2_gwconstituentr_gw_constitution_rela_a0156ac6_fk_gwml2_mec
			references gwml2_mechanismtype
				deferrable initially deferred
);

alter table gwml2_gwconstituentrelation owner to geonode;

create index if not exists gwml2_gwconstituentrelatio_gw_constituent_relation_ty_841bd855
	on gwml2_gwconstituentrelation (gw_constituent_relation_type_id);

create index if not exists gwml2_gwconstituentrelatio_gw_constitution_relation_m_a0156ac6
	on gwml2_gwconstituentrelation (gw_constitution_relation_mechanism_id);

create table if not exists gwml2_gwfluidbody_gw_background_constituent
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_background_constituent_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_1b783085_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwconstituent_id integer not null
		constraint gwml2_gwfluidbody_gw_gwconstituent_id_e52ea9e1_fk_gwml2_gwc
			references gwml2_gwconstituent
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bac_gwfluidbody_id_gwconstit_516e895d_uniq
		unique (gwfluidbody_id, gwconstituent_id)
);

alter table gwml2_gwfluidbody_gw_background_constituent owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_backg_gwfluidbody_id_1b783085
	on gwml2_gwfluidbody_gw_background_constituent (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_backg_gwconstituent_id_e52ea9e1
	on gwml2_gwfluidbody_gw_background_constituent (gwconstituent_id);

create table if not exists gwml2_gwfluidbody_gw_body_constituent
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_constituent_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_6ca3f7ca_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwmixtureconstituent_id integer not null
		constraint gwml2_gwfluidbody_gw_gwmixtureconstituent_77a97eba_fk_gwml2_gwm
			references gwml2_gwmixtureconstituent
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_gwmixture_5e1cb044_uniq
		unique (gwfluidbody_id, gwmixtureconstituent_id)
);

alter table gwml2_gwfluidbody_gw_body_constituent owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_constituent_gwfluidbody_id_6ca3f7ca
	on gwml2_gwfluidbody_gw_body_constituent (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body__gwmixtureconstituent_id_77a97eba
	on gwml2_gwfluidbody_gw_body_constituent (gwmixtureconstituent_id);

create table if not exists gwml2_gwfluidbody_gw_body_property
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_property_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_9cf305f7_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwfluidbodyproperty_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbodyproperty__61309bc7_fk_gwml2_gwf
			references gwml2_gwfluidbodyproperty
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_gwfluidbo_f229168b_uniq
		unique (gwfluidbody_id, gwfluidbodyproperty_id)
);

alter table gwml2_gwfluidbody_gw_body_property owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_property_gwfluidbody_id_9cf305f7
	on gwml2_gwfluidbody_gw_body_property (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body__gwfluidbodyproperty_id_61309bc7
	on gwml2_gwfluidbody_gw_body_property (gwfluidbodyproperty_id);

create table if not exists gwml2_gwfluidbody_gw_body_surface
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_surface_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_01c1c6c0_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwfluidbodysurface_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbodysurface_i_83903a77_fk_gwml2_gwf
			references gwml2_gwfluidbodysurface
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_gwfluidbo_32f1b61f_uniq
		unique (gwfluidbody_id, gwfluidbodysurface_id)
);

alter table gwml2_gwfluidbody_gw_body_surface owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_surface_gwfluidbody_id_01c1c6c0
	on gwml2_gwfluidbody_gw_body_surface (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body__gwfluidbodysurface_id_83903a77
	on gwml2_gwfluidbody_gw_body_surface (gwfluidbodysurface_id);

create table if not exists gwml2_gwconstituteof
(
	id serial not null
		constraint gwml2_gwconstituteof_pkey
			primary key,
	gw_constituent_id integer not null
		constraint gwml2_gwconstituteof_gw_constituent_id_d2cf033f_fk_gwml2_gwc
			references gwml2_gwconstituent
				deferrable initially deferred,
	gw_constituent_relation_id integer not null
		constraint gwml2_gwconstituteof_gw_constituent_relat_9f2278d7_fk_gwml2_gwc
			references gwml2_gwconstituentrelation
				deferrable initially deferred
);

alter table gwml2_gwconstituteof owner to geonode;

alter table gwml2_gwconstituent
	add constraint gwml2_gwconstituent_gw_constitute_of_id_bda33346_fk_gwml2_gwc
		foreign key (gw_constitute_of_id) references gwml2_gwconstituteof
			deferrable initially deferred;

create index if not exists gwml2_gwconstituteof_gw_constituent_id_d2cf033f
	on gwml2_gwconstituteof (gw_constituent_id);

create index if not exists gwml2_gwconstituteof_gw_constituent_relation_id_9f2278d7
	on gwml2_gwconstituteof (gw_constituent_relation_id);

create table if not exists gwml2_sitetype
(
	id serial not null
		constraint gwml2_sitetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_sitetype owner to geonode;

create table if not exists gwml2_gwmonitoringsite
(
	id serial not null
		constraint gwml2_gwmonitoringsite_pkey
			primary key,
	gw_site_name text,
	gw_site_location geometry(Point,4326) not null,
	gw_site_type_id integer
		constraint gwml2_gwmonitoringsi_gw_site_type_id_80bd7208_fk_gwml2_sit
			references gwml2_sitetype
				deferrable initially deferred
);

alter table gwml2_gwmonitoringsite owner to geonode;

create index if not exists gwml2_gwmonitoringsite_gw_site_location_id
	on gwml2_gwmonitoringsite (gw_site_location);

create index if not exists gwml2_gwmonitoringsite_gw_site_type_id_80bd7208
	on gwml2_gwmonitoringsite (gw_site_type_id);

create table if not exists gwml2_gwmonitoringsite_gw_site_reference_elevation
(
	id serial not null
		constraint gwml2_gwmonitoringsite_gw_site_reference_elevation_pkey
			primary key,
	gwmonitoringsite_id integer not null
		constraint gwml2_gwmonitoringsi_gwmonitoringsite_id_392df3e8_fk_gwml2_gwm
			references gwml2_gwmonitoringsite
				deferrable initially deferred,
	elevation_id integer not null
		constraint gwml2_gwmonitoringsi_elevation_id_e90be910_fk_gwml2_ele
			references gwml2_elevation
				deferrable initially deferred,
	constraint gwml2_gwmonitoringsite_g_gwmonitoringsite_id_elev_dc1bc648_uniq
		unique (gwmonitoringsite_id, elevation_id)
);

alter table gwml2_gwmonitoringsite_gw_site_reference_elevation owner to geonode;

create index if not exists gwml2_gwmonitoringsite_gw__gwmonitoringsite_id_392df3e8
	on gwml2_gwmonitoringsite_gw_site_reference_elevation (gwmonitoringsite_id);

create index if not exists gwml2_gwmonitoringsite_gw__elevation_id_e90be910
	on gwml2_gwmonitoringsite_gw_site_reference_elevation (elevation_id);

create table if not exists gwml2_documentcitation
(
	id serial not null
		constraint gwml2_documentcitation_pkey
			primary key,
	name text not null,
	date date,
	link text
);

alter table gwml2_documentcitation owner to geonode;

create table if not exists gwml2_environmentaldomaintypeterm
(
	id serial not null
		constraint gwml2_environmentaldomaintypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_environmentaldomaintypeterm owner to geonode;

create table if not exists gwml2_managementareatypeterm
(
	id serial not null
		constraint gwml2_managementareatypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_managementareatypeterm owner to geonode;

create table if not exists gwml2_specialisedzoneareatypeterm
(
	id serial not null
		constraint gwml2_specialisedzoneareatypeterm_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_specialisedzoneareatypeterm owner to geonode;

create table if not exists gwml2_yieldtype
(
	id serial not null
		constraint gwml2_yieldtype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_yieldtype owner to geonode;

create table if not exists gwml2_gwyield
(
	id serial not null
		constraint gwml2_gwyield_pkey
			primary key,
	gw_yield_id integer
		constraint gwml2_gwyield_gw_yield_id_510ee769_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	gw_yield_type_id integer
		constraint gwml2_gwyield_gw_yield_type_id_1f6fe4d1_fk_gwml2_yieldtype_id
			references gwml2_yieldtype
				deferrable initially deferred
);

alter table gwml2_gwyield owner to geonode;

create table if not exists gwml2_gwwell
(
	id serial not null
		constraint gwml2_gwwell_pkey
			primary key,
	gw_well_name text not null,
	gw_well_location geometry(Point,4326) not null,
	gw_well_contribution_zone geometry(Geometry,4326),
	gw_well_total_length double precision,
	gw_well_constructed_depth_id integer
		constraint gwml2_gwwell_gw_well_constructed_depth_id_key
			unique
		constraint gwml2_gwwell_gw_well_constructed__c45f26b1_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_well_construction_id integer
		constraint gwml2_gwwell_gw_well_construction_0c14cc72_fk_gwml2_bor
			references gwml2_borehole
				deferrable initially deferred,
	gw_well_licence_id integer
		constraint gwml2_gwwell_gw_well_licence_id_key
			unique
		constraint gwml2_gwwell_gw_well_licence_id_9879a016_fk_gwml2_gwlicence_id
			references gwml2_gwlicence
				deferrable initially deferred,
	gw_well_static_water_depth_id integer
		constraint gwml2_gwwell_gw_well_static_water_depth_id_key
			unique
		constraint gwml2_gwwell_gw_well_static_water_09ad2c8e_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_well_status_id integer
		constraint gwml2_gwwell_gw_well_status_id_e8797d9f_fk_gwml2_wel
			references gwml2_wellstatustypeterm
				deferrable initially deferred,
	gw_well_body_id integer
		constraint gwml2_gwwell_gw_well_body_id_9506b9f2_fk_gwml2_gwfluidbody_id
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gw_well_yield_id integer
		constraint gwml2_gwwell_gw_well_yield_id_c54fedd7_fk_gwml2_gwyield_id
			references gwml2_gwyield
				deferrable initially deferred
);

alter table gwml2_gwwell owner to geonode;

create index if not exists gwml2_gwwell_gw_well_location_id
	on gwml2_gwwell (gw_well_location);

create index if not exists gwml2_gwwell_gw_well_contribution_zone_id
	on gwml2_gwwell (gw_well_contribution_zone);

create index if not exists gwml2_gwwell_gw_well_construction_id_0c14cc72
	on gwml2_gwwell (gw_well_construction_id);

create index if not exists gwml2_gwwell_gw_well_status_id_e8797d9f
	on gwml2_gwwell (gw_well_status_id);

create index if not exists gwml2_gwwell_gw_well_body_id_9506b9f2
	on gwml2_gwwell (gw_well_body_id);

create index if not exists gwml2_gwwell_gw_well_yield_id_c54fedd7
	on gwml2_gwwell (gw_well_yield_id);

create table if not exists gwml2_gwgeologylog
(
	id serial not null
		constraint gwml2_gwgeologylog_pkey
			primary key,
	phenomenon_time timestamp with time zone,
	result_time timestamp with time zone,
	gw_level double precision,
	reference text,
	end_depth_id integer
		constraint gwml2_gwgeologylog_end_depth_id_c1477caa_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	gw_well_id integer
		constraint gwml2_gwgeologylog_gw_well_id_f666ee8f_fk_gwml2_gwwell_id
			references gwml2_gwwell
				deferrable initially deferred,
	start_depth_id integer
		constraint gwml2_gwgeologylog_start_depth_id_ac595dc7_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	"resultQuality" text,
	valid_time_id integer
		constraint gwml2_gwgeologylog_valid_time_id_5787349a_fk_gwml2_tmperiod_id
			references gwml2_tmperiod
				deferrable initially deferred
);

alter table gwml2_gwgeologylog owner to geonode;

create index if not exists gwml2_gwgeologylog_end_depth_id_c1477caa
	on gwml2_gwgeologylog (end_depth_id);

create index if not exists gwml2_gwgeologylog_gw_well_id_f666ee8f
	on gwml2_gwgeologylog (gw_well_id);

create index if not exists gwml2_gwgeologylog_start_depth_id_ac595dc7
	on gwml2_gwgeologylog (start_depth_id);

create index if not exists gwml2_gwgeologylog_valid_time_id_5787349a
	on gwml2_gwgeologylog (valid_time_id);

create table if not exists gwml2_gwgeologylog_parameter
(
	id serial not null
		constraint gwml2_gwgeologylog_parameter_pkey
			primary key,
	gwgeologylog_id integer not null
		constraint gwml2_gwgeologylog_p_gwgeologylog_id_92bfca87_fk_gwml2_gwg
			references gwml2_gwgeologylog
				deferrable initially deferred,
	namedvalue_id integer not null
		constraint gwml2_gwgeologylog_p_namedvalue_id_2a82cdcb_fk_gwml2_nam
			references gwml2_namedvalue
				deferrable initially deferred,
	constraint gwml2_gwgeologylog_param_gwgeologylog_id_namedval_388fb1ed_uniq
		unique (gwgeologylog_id, namedvalue_id)
);

alter table gwml2_gwgeologylog_parameter owner to geonode;

create index if not exists gwml2_gwgeologylog_parameter_gwgeologylog_id_92bfca87
	on gwml2_gwgeologylog_parameter (gwgeologylog_id);

create index if not exists gwml2_gwgeologylog_parameter_namedvalue_id_2a82cdcb
	on gwml2_gwgeologylog_parameter (namedvalue_id);

create index if not exists gwml2_gwyield_gw_yield_id_510ee769
	on gwml2_gwyield (gw_yield_id);

create index if not exists gwml2_gwyield_gw_yield_type_id_1f6fe4d1
	on gwml2_gwyield (gw_yield_type_id);

create table if not exists gwml2_gwmanagementarea
(
	id serial not null
		constraint gwml2_gwmanagementarea_pkey
			primary key,
	gw_area_name text not null,
	gw_area_description text not null,
	gw_area_shape geometry(Geometry,4326) not null,
	documentation_id integer
		constraint gwml2_gwmanagementar_documentation_id_d4586fa9_fk_gwml2_doc
			references gwml2_documentcitation
				deferrable initially deferred,
	gw_area_designation_period_id integer
		constraint gwml2_gwmanagementar_gw_area_designation__b0264afe_fk_gwml2_tmp
			references gwml2_tmperiod
				deferrable initially deferred,
	gw_area_environmental_domain_id integer
		constraint gwml2_gwmanagementar_gw_area_environmenta_59facd63_fk_gwml2_env
			references gwml2_environmentaldomaintypeterm
				deferrable initially deferred,
	gw_area_specialised_area_type_id integer
		constraint gwml2_gwmanagementar_gw_area_specialised__666fbcbf_fk_gwml2_spe
			references gwml2_specialisedzoneareatypeterm
				deferrable initially deferred,
	gw_area_type_id integer
		constraint gwml2_gwmanagementar_gw_area_type_id_92fda7b6_fk_gwml2_man
			references gwml2_managementareatypeterm
				deferrable initially deferred,
	gw_area_yield_id integer
		constraint gwml2_gwmanagementar_gw_area_yield_id_403360c6_fk_gwml2_gwy
			references gwml2_gwyield
				deferrable initially deferred,
	related_management_area_id integer
		constraint gwml2_gwmanagementar_related_management_a_d8c8e254_fk_gwml2_gwm
			references gwml2_gwmanagementarea
				deferrable initially deferred
);

alter table gwml2_gwmanagementarea owner to geonode;

create index if not exists gwml2_gwmanagementarea_gw_area_shape_id
	on gwml2_gwmanagementarea (gw_area_shape);

create index if not exists gwml2_gwmanagementarea_documentation_id_d4586fa9
	on gwml2_gwmanagementarea (documentation_id);

create index if not exists gwml2_gwmanagementarea_gw_area_designation_period_id_b0264afe
	on gwml2_gwmanagementarea (gw_area_designation_period_id);

create index if not exists gwml2_gwmanagementarea_gw_area_environmental_domain_id_59facd63
	on gwml2_gwmanagementarea (gw_area_environmental_domain_id);

create index if not exists gwml2_gwmanagementarea_gw_area_specialised_area_t_666fbcbf
	on gwml2_gwmanagementarea (gw_area_specialised_area_type_id);

create index if not exists gwml2_gwmanagementarea_gw_area_type_id_92fda7b6
	on gwml2_gwmanagementarea (gw_area_type_id);

create index if not exists gwml2_gwmanagementarea_gw_area_yield_id_403360c6
	on gwml2_gwmanagementarea (gw_area_yield_id);

create index if not exists gwml2_gwmanagementarea_related_management_area_id_d8c8e254
	on gwml2_gwmanagementarea (related_management_area_id);

create table if not exists gwml2_gwmanagementarea_gw_area_body
(
	id serial not null
		constraint gwml2_gwmanagementarea_gw_area_body_pkey
			primary key,
	gwmanagementarea_id integer not null
		constraint gwml2_gwmanagementar_gwmanagementarea_id_e3f280b2_fk_gwml2_gwm
			references gwml2_gwmanagementarea
				deferrable initially deferred,
	gwfluidbody_id integer not null
		constraint gwml2_gwmanagementar_gwfluidbody_id_8e6daf18_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	constraint gwml2_gwmanagementarea_g_gwmanagementarea_id_gwfl_56b4582b_uniq
		unique (gwmanagementarea_id, gwfluidbody_id)
);

alter table gwml2_gwmanagementarea_gw_area_body owner to geonode;

create index if not exists gwml2_gwmanagementarea_gw__gwmanagementarea_id_e3f280b2
	on gwml2_gwmanagementarea_gw_area_body (gwmanagementarea_id);

create index if not exists gwml2_gwmanagementarea_gw_area_body_gwfluidbody_id_8e6daf18
	on gwml2_gwmanagementarea_gw_area_body (gwfluidbody_id);

create table if not exists gwml2_gwmanagementarea_gw_area_competent_authority
(
	id serial not null
		constraint gwml2_gwmanagementarea_gw_area_competent_authority_pkey
			primary key,
	gwmanagementarea_id integer not null
		constraint gwml2_gwmanagementar_gwmanagementarea_id_9d9a6d28_fk_gwml2_gwm
			references gwml2_gwmanagementarea
				deferrable initially deferred,
	ciresponsibleparty_id integer not null
		constraint gwml2_gwmanagementar_ciresponsibleparty_i_dcfac191_fk_gwml2_cir
			references gwml2_ciresponsibleparty
				deferrable initially deferred,
	constraint gwml2_gwmanagementarea_g_gwmanagementarea_id_cire_fb8f6ecd_uniq
		unique (gwmanagementarea_id, ciresponsibleparty_id)
);

alter table gwml2_gwmanagementarea_gw_area_competent_authority owner to geonode;

create index if not exists gwml2_gwmanagementarea_gw__gwmanagementarea_id_9d9a6d28
	on gwml2_gwmanagementarea_gw_area_competent_authority (gwmanagementarea_id);

create index if not exists gwml2_gwmanagementarea_gw__ciresponsibleparty_id_dcfac191
	on gwml2_gwmanagementarea_gw_area_competent_authority (ciresponsibleparty_id);

create table if not exists gwml2_gwunitvoidproperty
(
	id serial not null
		constraint gwml2_gwunitvoidproperty_pkey
			primary key
);

alter table gwml2_gwunitvoidproperty owner to geonode;

create table if not exists gwml2_gwunitvoidproperty_gw_permeability
(
	id serial not null
		constraint gwml2_gwunitvoidproperty_gw_permeability_pkey
			primary key,
	gwunitvoidproperty_id integer not null
		constraint gwml2_gwunitvoidprop_gwunitvoidproperty_i_6846a5c3_fk_gwml2_gwu
			references gwml2_gwunitvoidproperty
				deferrable initially deferred,
	quantity_id integer not null
		constraint gwml2_gwunitvoidprop_quantity_id_3dbbd799_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	constraint gwml2_gwunitvoidproperty_gwunitvoidproperty_id_qu_f3f07e7f_uniq
		unique (gwunitvoidproperty_id, quantity_id)
);

alter table gwml2_gwunitvoidproperty_gw_permeability owner to geonode;

create index if not exists gwml2_gwunitvoidproperty_g_gwunitvoidproperty_id_6846a5c3
	on gwml2_gwunitvoidproperty_gw_permeability (gwunitvoidproperty_id);

create index if not exists gwml2_gwunitvoidproperty_gw_permeability_quantity_id_3dbbd799
	on gwml2_gwunitvoidproperty_gw_permeability (quantity_id);

create table if not exists gwml2_gwunitvoidproperty_gw_porosity
(
	id serial not null
		constraint gwml2_gwunitvoidproperty_gw_porosity_pkey
			primary key,
	gwunitvoidproperty_id integer not null
		constraint gwml2_gwunitvoidprop_gwunitvoidproperty_i_dc2c05a9_fk_gwml2_gwu
			references gwml2_gwunitvoidproperty
				deferrable initially deferred,
	gwporosity_id integer not null
		constraint gwml2_gwunitvoidprop_gwporosity_id_cfb3f1fb_fk_gwml2_gwp
			references gwml2_gwporosity
				deferrable initially deferred,
	constraint gwml2_gwunitvoidproperty_gwunitvoidproperty_id_gw_65bb0406_uniq
		unique (gwunitvoidproperty_id, gwporosity_id)
);

alter table gwml2_gwunitvoidproperty_gw_porosity owner to geonode;

create index if not exists gwml2_gwunitvoidproperty_g_gwunitvoidproperty_id_dc2c05a9
	on gwml2_gwunitvoidproperty_gw_porosity (gwunitvoidproperty_id);

create index if not exists gwml2_gwunitvoidproperty_gw_porosity_gwporosity_id_cfb3f1fb
	on gwml2_gwunitvoidproperty_gw_porosity (gwporosity_id);

create table if not exists gwml2_gwunitfluidproperty
(
	id serial not null
		constraint gwml2_gwunitfluidproperty_pkey
			primary key
);

alter table gwml2_gwunitfluidproperty owner to geonode;

create table if not exists gwml2_glearthmaterial
(
	id serial not null
		constraint gwml2_glearthmaterial_pkey
			primary key,
	gw_fluid_property_id integer
		constraint gwml2_glearthmateria_gw_fluid_property_id_205f159c_fk_gwml2_gwu
			references gwml2_gwunitfluidproperty
				deferrable initially deferred,
	gw_void_property_id integer
		constraint gwml2_glearthmateria_gw_void_property_id_6f7df3ae_fk_gwml2_gwu
			references gwml2_gwunitvoidproperty
				deferrable initially deferred
);

alter table gwml2_glearthmaterial owner to geonode;

create index if not exists gwml2_glearthmaterial_gw_fluid_property_id_205f159c
	on gwml2_glearthmaterial (gw_fluid_property_id);

create index if not exists gwml2_glearthmaterial_gw_void_property_id_6f7df3ae
	on gwml2_glearthmaterial (gw_void_property_id);

create table if not exists gwml2_gwunitfluidproperty_gw_hydraulic_conductivity
(
	id serial not null
		constraint gwml2_gwunitfluidproperty_gw_hydraulic_conductivity_pkey
			primary key,
	gwunitfluidproperty_id integer not null
		constraint gwml2_gwunitfluidpro_gwunitfluidproperty__f3dd67ea_fk_gwml2_gwu
			references gwml2_gwunitfluidproperty
				deferrable initially deferred,
	quantity_id integer not null
		constraint gwml2_gwunitfluidpro_quantity_id_1c774654_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	constraint gwml2_gwunitfluidpropert_gwunitfluidproperty_id_q_6d2e7882_uniq
		unique (gwunitfluidproperty_id, quantity_id)
);

alter table gwml2_gwunitfluidproperty_gw_hydraulic_conductivity owner to geonode;

create index if not exists gwml2_gwunitfluidproperty__gwunitfluidproperty_id_f3dd67ea
	on gwml2_gwunitfluidproperty_gw_hydraulic_conductivity (gwunitfluidproperty_id);

create index if not exists gwml2_gwunitfluidproperty__quantity_id_1c774654
	on gwml2_gwunitfluidproperty_gw_hydraulic_conductivity (quantity_id);

create table if not exists gwml2_gwunitfluidproperty_gw_storativity
(
	id serial not null
		constraint gwml2_gwunitfluidproperty_gw_storativity_pkey
			primary key,
	gwunitfluidproperty_id integer not null
		constraint gwml2_gwunitfluidpro_gwunitfluidproperty__63c47e2f_fk_gwml2_gwu
			references gwml2_gwunitfluidproperty
				deferrable initially deferred,
	quantity_id integer not null
		constraint gwml2_gwunitfluidpro_quantity_id_401f28a2_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	constraint gwml2_gwunitfluidpropert_gwunitfluidproperty_id_q_2cedaf49_uniq
		unique (gwunitfluidproperty_id, quantity_id)
);

alter table gwml2_gwunitfluidproperty_gw_storativity owner to geonode;

create index if not exists gwml2_gwunitfluidproperty__gwunitfluidproperty_id_63c47e2f
	on gwml2_gwunitfluidproperty_gw_storativity (gwunitfluidproperty_id);

create index if not exists gwml2_gwunitfluidproperty_gw_storativity_quantity_id_401f28a2
	on gwml2_gwunitfluidproperty_gw_storativity (quantity_id);

create table if not exists gwml2_gwunitfluidproperty_gw_transmissivity
(
	id serial not null
		constraint gwml2_gwunitfluidproperty_gw_transmissivity_pkey
			primary key,
	gwunitfluidproperty_id integer not null
		constraint gwml2_gwunitfluidpro_gwunitfluidproperty__b8ce801b_fk_gwml2_gwu
			references gwml2_gwunitfluidproperty
				deferrable initially deferred,
	quantity_id integer not null
		constraint gwml2_gwunitfluidpro_quantity_id_79a3d180_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	constraint gwml2_gwunitfluidpropert_gwunitfluidproperty_id_q_f43c9f55_uniq
		unique (gwunitfluidproperty_id, quantity_id)
);

alter table gwml2_gwunitfluidproperty_gw_transmissivity owner to geonode;

create index if not exists gwml2_gwunitfluidproperty__gwunitfluidproperty_id_b8ce801b
	on gwml2_gwunitfluidproperty_gw_transmissivity (gwunitfluidproperty_id);

create index if not exists gwml2_gwunitfluidproperty__quantity_id_79a3d180
	on gwml2_gwunitfluidproperty_gw_transmissivity (quantity_id);

create table if not exists gwml2_gwunitfluidproperty_gw_yield
(
	id serial not null
		constraint gwml2_gwunitfluidproperty_gw_yield_pkey
			primary key,
	gwunitfluidproperty_id integer not null
		constraint gwml2_gwunitfluidpro_gwunitfluidproperty__ca2c8bfe_fk_gwml2_gwu
			references gwml2_gwunitfluidproperty
				deferrable initially deferred,
	gwyield_id integer not null
		constraint gwml2_gwunitfluidpro_gwyield_id_24522a49_fk_gwml2_gwy
			references gwml2_gwyield
				deferrable initially deferred,
	constraint gwml2_gwunitfluidpropert_gwunitfluidproperty_id_g_63e57e82_uniq
		unique (gwunitfluidproperty_id, gwyield_id)
);

alter table gwml2_gwunitfluidproperty_gw_yield owner to geonode;

create index if not exists gwml2_gwunitfluidproperty__gwunitfluidproperty_id_ca2c8bfe
	on gwml2_gwunitfluidproperty_gw_yield (gwunitfluidproperty_id);

create index if not exists gwml2_gwunitfluidproperty_gw_yield_gwyield_id_24522a49
	on gwml2_gwunitfluidproperty_gw_yield (gwyield_id);

create table if not exists gwml2_gwhydrogeovoid
(
	id serial not null
		constraint gwml2_gwhydrogeovoid_pkey
			primary key,
	gw_void_description text,
	gw_void_shape geometry(Geometry,4326),
	gw_fluid_body_void_id integer
		constraint gwml2_gwhydrogeovoid_gw_fluid_body_void_i_5ab182f6_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gw_part_of_void_id integer
		constraint gwml2_gwhydrogeovoid_gw_part_of_void_id_aad30c79_fk_gwml2_gwh
			references gwml2_gwhydrogeovoid
				deferrable initially deferred,
	gw_void_type_id integer
		constraint gwml2_gwhydrogeovoid_gw_void_type_id_0f618838_fk_gwml2_por
			references gwml2_porositytypeterm
				deferrable initially deferred,
	gw_void_volume_id integer
		constraint gwml2_gwhydrogeovoid_gw_void_volume_id_907c91cc_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_void_metadata_id integer
		constraint gwml2_gwhydrogeovoid_gw_void_metadata_id_82e950cb_fk_gwml2_gwm
			references gwml2_gwmetadata
				deferrable initially deferred
);

alter table gwml2_gwhydrogeovoid owner to geonode;

create index if not exists gwml2_gwhydrogeovoid_gw_void_shape_id
	on gwml2_gwhydrogeovoid (gw_void_shape);

create index if not exists gwml2_gwhydrogeovoid_gw_fluid_body_void_id_5ab182f6
	on gwml2_gwhydrogeovoid (gw_fluid_body_void_id);

create index if not exists gwml2_gwhydrogeovoid_gw_part_of_void_id_aad30c79
	on gwml2_gwhydrogeovoid (gw_part_of_void_id);

create index if not exists gwml2_gwhydrogeovoid_gw_void_type_id_0f618838
	on gwml2_gwhydrogeovoid (gw_void_type_id);

create index if not exists gwml2_gwhydrogeovoid_gw_void_volume_id_907c91cc
	on gwml2_gwhydrogeovoid (gw_void_volume_id);

create index if not exists gwml2_gwhydrogeovoid_gw_void_metadata_id_82e950cb
	on gwml2_gwhydrogeovoid (gw_void_metadata_id);

create table if not exists gwml2_gwhydrogeovoid_gw_void_host_material
(
	id serial not null
		constraint gwml2_gwhydrogeovoid_gw_void_host_material_pkey
			primary key,
	gwhydrogeovoid_id integer not null
		constraint gwml2_gwhydrogeovoid_gwhydrogeovoid_id_47ec9a85_fk_gwml2_gwh
			references gwml2_gwhydrogeovoid
				deferrable initially deferred,
	glearthmaterial_id integer not null
		constraint gwml2_gwhydrogeovoid_glearthmaterial_id_7f434a76_fk_gwml2_gle
			references gwml2_glearthmaterial
				deferrable initially deferred,
	constraint gwml2_gwhydrogeovoid_gw__gwhydrogeovoid_id_gleart_3bf28191_uniq
		unique (gwhydrogeovoid_id, glearthmaterial_id)
);

alter table gwml2_gwhydrogeovoid_gw_void_host_material owner to geonode;

create index if not exists gwml2_gwhydrogeovoid_gw_vo_gwhydrogeovoid_id_47ec9a85
	on gwml2_gwhydrogeovoid_gw_void_host_material (gwhydrogeovoid_id);

create index if not exists gwml2_gwhydrogeovoid_gw_vo_glearthmaterial_id_7f434a76
	on gwml2_gwhydrogeovoid_gw_void_host_material (glearthmaterial_id);

create table if not exists gwml2_temporaltype
(
	id serial not null
		constraint gwml2_temporaltype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_temporaltype owner to geonode;

create table if not exists gwml2_gwflow
(
	id serial not null
		constraint gwml2_gwflow_pkey
			primary key,
	gw_flow_time_id integer
		constraint gwml2_gwflow_gw_flow_time_id_b429b982_fk_gwml2_temporaltype_id
			references gwml2_temporaltype
				deferrable initially deferred,
	gw_flow_persistence_id integer
		constraint gwml2_gwflow_gw_flow_persistence__26e55600_fk_gwml2_flo
			references gwml2_flowpersistencetype
				deferrable initially deferred,
	gw_flow_process_id integer
		constraint gwml2_gwflow_gw_flow_process_id_f3ba682a_fk_gwml2_wat
			references gwml2_waterflowprocess
				deferrable initially deferred,
	gw_flow_system_id integer
		constraint gwml2_gwflow_gw_flow_system_id_040cf9fa_fk_gwml2_gwf
			references gwml2_gwflowsystem
				deferrable initially deferred,
	gw_flow_velocity_id integer
		constraint gwml2_gwflow_gw_flow_velocity_id_key
			unique
		constraint gwml2_gwflow_gw_flow_velocity_id_cd9d1bae_fk_gwml2_quantity_id
			references gwml2_quantity
				deferrable initially deferred,
	gw_flow_volume_rate_id integer
		constraint gwml2_gwflow_gw_flow_volume_rate_id_key
			unique
		constraint gwml2_gwflow_gw_flow_volume_rate__a0141b3f_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred
);

alter table gwml2_gwflow owner to geonode;

create index if not exists gwml2_gwflow_gw_flow_process_id_f3ba682a
	on gwml2_gwflow (gw_flow_process_id);

create index if not exists gwml2_gwflow_gw_flow_system_id_040cf9fa
	on gwml2_gwflow (gw_flow_system_id);

create index if not exists gwml2_gwflow_gw_flow_persistence_id_26e55600
	on gwml2_gwflow (gw_flow_persistence_id);

create index if not exists gwml2_gwflow_gw_flow_time_id_b429b982
	on gwml2_gwflow (gw_flow_time_id);

create table if not exists gwml2_gwwaterbudget
(
	id serial not null
		constraint gwml2_gwwaterbudget_pkey
			primary key,
	gw_budget_amount_id integer
		constraint gwml2_gwwaterbudget_gw_budget_amount_id_c655e3a8_fk_gwml2_qua
			references gwml2_quantity
				deferrable initially deferred,
	gw_budget_valid_time_id integer
		constraint gwml2_gwwaterbudget_gw_budget_valid_time_9d315cb8_fk_gwml2_tem
			references gwml2_temporaltype
				deferrable initially deferred
);

alter table gwml2_gwwaterbudget owner to geonode;

create index if not exists gwml2_gwwaterbudget_gw_budget_amount_id_c655e3a8
	on gwml2_gwwaterbudget (gw_budget_amount_id);

create index if not exists gwml2_gwwaterbudget_gw_budget_valid_time_id_9d315cb8
	on gwml2_gwwaterbudget (gw_budget_valid_time_id);

create table if not exists gwml2_gwwaterbudget_gw_budget_discharge
(
	id serial not null
		constraint gwml2_gwwaterbudget_gw_budget_discharge_pkey
			primary key,
	gwwaterbudget_id integer not null
		constraint gwml2_gwwaterbudget__gwwaterbudget_id_b362993d_fk_gwml2_gww
			references gwml2_gwwaterbudget
				deferrable initially deferred,
	gwdischarge_id integer not null
		constraint gwml2_gwwaterbudget__gwdischarge_id_be947e9d_fk_gwml2_gwd
			references gwml2_gwdischarge
				deferrable initially deferred,
	constraint gwml2_gwwaterbudget_gw_b_gwwaterbudget_id_gwdisch_a9f3d02f_uniq
		unique (gwwaterbudget_id, gwdischarge_id)
);

alter table gwml2_gwwaterbudget_gw_budget_discharge owner to geonode;

create index if not exists gwml2_gwwaterbudget_gw_bud_gwwaterbudget_id_b362993d
	on gwml2_gwwaterbudget_gw_budget_discharge (gwwaterbudget_id);

create index if not exists gwml2_gwwaterbudget_gw_budget_discharge_gwdischarge_id_be947e9d
	on gwml2_gwwaterbudget_gw_budget_discharge (gwdischarge_id);

create table if not exists gwml2_gwwaterbudget_gw_budget_recharge
(
	id serial not null
		constraint gwml2_gwwaterbudget_gw_budget_recharge_pkey
			primary key,
	gwwaterbudget_id integer not null
		constraint gwml2_gwwaterbudget__gwwaterbudget_id_a990b1eb_fk_gwml2_gww
			references gwml2_gwwaterbudget
				deferrable initially deferred,
	gwrecharge_id integer not null
		constraint gwml2_gwwaterbudget__gwrecharge_id_3d18800b_fk_gwml2_gwr
			references gwml2_gwrecharge
				deferrable initially deferred,
	constraint gwml2_gwwaterbudget_gw_b_gwwaterbudget_id_gwrecha_c8d58d77_uniq
		unique (gwwaterbudget_id, gwrecharge_id)
);

alter table gwml2_gwwaterbudget_gw_budget_recharge owner to geonode;

create index if not exists gwml2_gwwaterbudget_gw_bud_gwwaterbudget_id_a990b1eb
	on gwml2_gwwaterbudget_gw_budget_recharge (gwwaterbudget_id);

create index if not exists gwml2_gwwaterbudget_gw_budget_recharge_gwrecharge_id_3d18800b
	on gwml2_gwwaterbudget_gw_budget_recharge (gwrecharge_id);

create table if not exists gwml2_gwhydrogeounit
(
	id serial not null
		constraint gwml2_gwhydrogeounit_pkey
			primary key,
	gw_unit_media_id integer
		constraint gwml2_gwhydrogeounit_gw_unit_media_id_690a8541_fk_gwml2_por
			references gwml2_porositytypeterm
				deferrable initially deferred,
	gw_unit_water_budget_id integer
		constraint gwml2_gwhydrogeounit_gw_unit_water_budget_d0764e3c_fk_gwml2_gww
			references gwml2_gwwaterbudget
				deferrable initially deferred
);

alter table gwml2_gwhydrogeounit owner to geonode;

create index if not exists gwml2_gwhydrogeounit_gw_unit_media_id_690a8541
	on gwml2_gwhydrogeounit (gw_unit_media_id);

create index if not exists gwml2_gwhydrogeounit_gw_unit_water_budget_id_d0764e3c
	on gwml2_gwhydrogeounit (gw_unit_water_budget_id);

create table if not exists gwml2_gwhydrogeounit_gw_unit_discharge
(
	id serial not null
		constraint gwml2_gwhydrogeounit_gw_unit_discharge_pkey
			primary key,
	gwhydrogeounit_id integer not null
		constraint gwml2_gwhydrogeounit_gwhydrogeounit_id_9f0bb928_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	gwdischarge_id integer not null
		constraint gwml2_gwhydrogeounit_gwdischarge_id_bed0b609_fk_gwml2_gwd
			references gwml2_gwdischarge
				deferrable initially deferred,
	constraint gwml2_gwhydrogeounit_gw__gwhydrogeounit_id_gwdisc_cec64a02_uniq
		unique (gwhydrogeounit_id, gwdischarge_id)
);

alter table gwml2_gwhydrogeounit_gw_unit_discharge owner to geonode;

create index if not exists gwml2_gwhydrogeounit_gw_un_gwhydrogeounit_id_9f0bb928
	on gwml2_gwhydrogeounit_gw_unit_discharge (gwhydrogeounit_id);

create index if not exists gwml2_gwhydrogeounit_gw_unit_discharge_gwdischarge_id_bed0b609
	on gwml2_gwhydrogeounit_gw_unit_discharge (gwdischarge_id);

create table if not exists gwml2_gwhydrogeounit_gw_unit_recharge
(
	id serial not null
		constraint gwml2_gwhydrogeounit_gw_unit_recharge_pkey
			primary key,
	gwhydrogeounit_id integer not null
		constraint gwml2_gwhydrogeounit_gwhydrogeounit_id_54d4c9a5_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	gwrecharge_id integer not null
		constraint gwml2_gwhydrogeounit_gwrecharge_id_d557cd72_fk_gwml2_gwr
			references gwml2_gwrecharge
				deferrable initially deferred,
	constraint gwml2_gwhydrogeounit_gw__gwhydrogeounit_id_gwrech_5035369d_uniq
		unique (gwhydrogeounit_id, gwrecharge_id)
);

alter table gwml2_gwhydrogeounit_gw_unit_recharge owner to geonode;

create index if not exists gwml2_gwhydrogeounit_gw_un_gwhydrogeounit_id_54d4c9a5
	on gwml2_gwhydrogeounit_gw_unit_recharge (gwhydrogeounit_id);

create index if not exists gwml2_gwhydrogeounit_gw_unit_recharge_gwrecharge_id_d557cd72
	on gwml2_gwhydrogeounit_gw_unit_recharge (gwrecharge_id);

create table if not exists gwml2_gwhydrogeounit_gw_unit_vulnerability
(
	id serial not null
		constraint gwml2_gwhydrogeounit_gw_unit_vulnerability_pkey
			primary key,
	gwhydrogeounit_id integer not null
		constraint gwml2_gwhydrogeounit_gwhydrogeounit_id_349fcfaf_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	gwvulnerability_id integer not null
		constraint gwml2_gwhydrogeounit_gwvulnerability_id_8840a050_fk_gwml2_gwv
			references gwml2_gwvulnerability
				deferrable initially deferred,
	constraint gwml2_gwhydrogeounit_gw__gwhydrogeounit_id_gwvuln_51f9d8f2_uniq
		unique (gwhydrogeounit_id, gwvulnerability_id)
);

alter table gwml2_gwhydrogeounit_gw_unit_vulnerability owner to geonode;

create index if not exists gwml2_gwhydrogeounit_gw_un_gwhydrogeounit_id_349fcfaf
	on gwml2_gwhydrogeounit_gw_unit_vulnerability (gwhydrogeounit_id);

create index if not exists gwml2_gwhydrogeounit_gw_un_gwvulnerability_id_8840a050
	on gwml2_gwhydrogeounit_gw_unit_vulnerability (gwvulnerability_id);

create table if not exists gwml2_gwhydrogeounit_properties
(
	id serial not null
		constraint gwml2_gwhydrogeounit_properties_pkey
			primary key,
	gwhydrogeounit_id integer not null
		constraint gwml2_gwhydrogeounit_gwhydrogeounit_id_97af89d1_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	gwunitproperties_id integer not null
		constraint gwml2_gwhydrogeounit_gwunitproperties_id_4e56f813_fk_gwml2_gwu
			references gwml2_gwunitproperties
				deferrable initially deferred,
	constraint gwml2_gwhydrogeounit_pro_gwhydrogeounit_id_gwunit_efd045d5_uniq
		unique (gwhydrogeounit_id, gwunitproperties_id)
);

alter table gwml2_gwhydrogeounit_properties owner to geonode;

create index if not exists gwml2_gwhydrogeounit_properties_gwhydrogeounit_id_97af89d1
	on gwml2_gwhydrogeounit_properties (gwhydrogeounit_id);

create index if not exists gwml2_gwhydrogeounit_properties_gwunitproperties_id_4e56f813
	on gwml2_gwhydrogeounit_properties (gwunitproperties_id);

create table if not exists gwml2_gwfluidbody_gw_body_flow
(
	id serial not null
		constraint gwml2_gwfluidbody_gw_body_flow_pkey
			primary key,
	gwfluidbody_id integer not null
		constraint gwml2_gwfluidbody_gw_gwfluidbody_id_c74c4027_fk_gwml2_gwf
			references gwml2_gwfluidbody
				deferrable initially deferred,
	gwflow_id integer not null
		constraint gwml2_gwfluidbody_gw_gwflow_id_550b6958_fk_gwml2_gwf
			references gwml2_gwflow
				deferrable initially deferred,
	constraint gwml2_gwfluidbody_gw_bod_gwfluidbody_id_gwflow_id_017ed410_uniq
		unique (gwfluidbody_id, gwflow_id)
);

alter table gwml2_gwfluidbody_gw_body_flow owner to geonode;

create index if not exists gwml2_gwfluidbody_gw_body_flow_gwfluidbody_id_c74c4027
	on gwml2_gwfluidbody_gw_body_flow (gwfluidbody_id);

create index if not exists gwml2_gwfluidbody_gw_body_flow_gwflow_id_550b6958
	on gwml2_gwfluidbody_gw_body_flow (gwflow_id);

create table if not exists gwml2_gwmanagementarea_gw_area_water_budget
(
	id serial not null
		constraint gwml2_gwmanagementarea_gw_area_water_budget_pkey
			primary key,
	gwmanagementarea_id integer not null
		constraint gwml2_gwmanagementar_gwmanagementarea_id_f41fa079_fk_gwml2_gwm
			references gwml2_gwmanagementarea
				deferrable initially deferred,
	gwwaterbudget_id integer not null
		constraint gwml2_gwmanagementar_gwwaterbudget_id_e268529a_fk_gwml2_gww
			references gwml2_gwwaterbudget
				deferrable initially deferred,
	constraint gwml2_gwmanagementarea_g_gwmanagementarea_id_gwwa_d004c683_uniq
		unique (gwmanagementarea_id, gwwaterbudget_id)
);

alter table gwml2_gwmanagementarea_gw_area_water_budget owner to geonode;

create index if not exists gwml2_gwmanagementarea_gw__gwmanagementarea_id_f41fa079
	on gwml2_gwmanagementarea_gw_area_water_budget (gwmanagementarea_id);

create index if not exists gwml2_gwmanagementarea_gw__gwwaterbudget_id_e268529a
	on gwml2_gwmanagementarea_gw_area_water_budget (gwwaterbudget_id);

create table if not exists gwml2_gwmanagementarea_gw_managed_unit
(
	id serial not null
		constraint gwml2_gwmanagementarea_gw_managed_unit_pkey
			primary key,
	gwmanagementarea_id integer not null
		constraint gwml2_gwmanagementar_gwmanagementarea_id_f5512a50_fk_gwml2_gwm
			references gwml2_gwmanagementarea
				deferrable initially deferred,
	gwhydrogeounit_id integer not null
		constraint gwml2_gwmanagementar_gwhydrogeounit_id_535e0e29_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	constraint gwml2_gwmanagementarea_g_gwmanagementarea_id_gwhy_8327a37d_uniq
		unique (gwmanagementarea_id, gwhydrogeounit_id)
);

alter table gwml2_gwmanagementarea_gw_managed_unit owner to geonode;

create index if not exists gwml2_gwmanagementarea_gw__gwmanagementarea_id_f5512a50
	on gwml2_gwmanagementarea_gw_managed_unit (gwmanagementarea_id);

create index if not exists gwml2_gwmanagementarea_gw__gwhydrogeounit_id_535e0e29
	on gwml2_gwmanagementarea_gw_managed_unit (gwhydrogeounit_id);

create table if not exists gwml2_gwvoidunit
(
	id serial not null
		constraint gwml2_gwvoidunit_pkey
			primary key,
	gw_hydrogeo_unit_id integer not null
		constraint gwml2_gwvoidunit_gw_hydrogeo_unit_id_83dad8a8_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	gw_unit_void_property_id integer not null
		constraint gwml2_gwvoidunit_gw_unit_void_propert_b4cc6f93_fk_gwml2_gwu
			references gwml2_gwunitvoidproperty
				deferrable initially deferred
);

alter table gwml2_gwvoidunit owner to geonode;

create table if not exists gwml2_gwhydrogeovoid_gw_void_unit
(
	id serial not null
		constraint gwml2_gwhydrogeovoid_gw_void_unit_pkey
			primary key,
	gwhydrogeovoid_id integer not null
		constraint gwml2_gwhydrogeovoid_gwhydrogeovoid_id_f3dd2ada_fk_gwml2_gwh
			references gwml2_gwhydrogeovoid
				deferrable initially deferred,
	gwvoidunit_id integer not null
		constraint gwml2_gwhydrogeovoid_gwvoidunit_id_cd774ad7_fk_gwml2_gwv
			references gwml2_gwvoidunit
				deferrable initially deferred,
	constraint gwml2_gwhydrogeovoid_gw__gwhydrogeovoid_id_gwhydr_42555129_uniq
		unique (gwhydrogeovoid_id, gwvoidunit_id)
);

alter table gwml2_gwhydrogeovoid_gw_void_unit owner to geonode;

create index if not exists gwml2_gwhydrogeovoid_gw_void_unit_gwhydrogeovoid_id_f3dd2ada
	on gwml2_gwhydrogeovoid_gw_void_unit (gwhydrogeovoid_id);

create index if not exists gwml2_gwhydrogeovoid_gw_void_unit_gwhydrogeounit_id_b356b699
	on gwml2_gwhydrogeovoid_gw_void_unit (gwvoidunit_id);

create index if not exists gwml2_gwvoidunit_gw_hydrogeo_unit_id_83dad8a8
	on gwml2_gwvoidunit (gw_hydrogeo_unit_id);

create index if not exists gwml2_gwvoidunit_gw_unit_void_property_id_b4cc6f93
	on gwml2_gwvoidunit (gw_unit_void_property_id);

create table if not exists gwml2_wellpurposetype
(
	id serial not null
		constraint gwml2_wellpurposetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_wellpurposetype owner to geonode;

create table if not exists gwml2_wellwaterusetype
(
	id serial not null
		constraint gwml2_wellwaterusetype_pkey
			primary key,
	name text,
	description text
);

alter table gwml2_wellwaterusetype owner to geonode;

create table if not exists "gwml2_gwwell_gwWellReferenceElevation"
(
	id serial not null
		constraint "gwml2_gwwell_gwWellReferenceElevation_pkey"
			primary key,
	gwwell_id integer not null
		constraint "gwml2_gwwell_gwWellR_gwwell_id_4ab095e0_fk_gwml2_gww"
			references gwml2_gwwell
				deferrable initially deferred,
	elevation_id integer not null
		constraint "gwml2_gwwell_gwWellR_elevation_id_cc232d96_fk_gwml2_ele"
			references gwml2_elevation
				deferrable initially deferred,
	constraint "gwml2_gwwell_gwWellRefer_gwwell_id_elevation_id_c8a873f3_uniq"
		unique (gwwell_id, elevation_id)
);

alter table "gwml2_gwwell_gwWellReferenceElevation" owner to geonode;

create index if not exists "gwml2_gwwell_gwWellReferenceElevation_gwwell_id_4ab095e0"
	on "gwml2_gwwell_gwWellReferenceElevation" (gwwell_id);

create index if not exists "gwml2_gwwell_gwWellReferenceElevation_elevation_id_cc232d96"
	on "gwml2_gwwell_gwWellReferenceElevation" (elevation_id);

create table if not exists gwml2_gwwell_gw_well_unit
(
	id serial not null
		constraint gwml2_gwwell_gw_well_unit_pkey
			primary key,
	gwwell_id integer not null
		constraint gwml2_gwwell_gw_well_unit_gwwell_id_30648c26_fk_gwml2_gwwell_id
			references gwml2_gwwell
				deferrable initially deferred,
	gwhydrogeounit_id integer not null
		constraint gwml2_gwwell_gw_well_gwhydrogeounit_id_50cb2836_fk_gwml2_gwh
			references gwml2_gwhydrogeounit
				deferrable initially deferred,
	constraint gwml2_gwwell_gw_well_uni_gwwell_id_gwhydrogeounit_e8e536c1_uniq
		unique (gwwell_id, gwhydrogeounit_id)
);

alter table gwml2_gwwell_gw_well_unit owner to geonode;

create index if not exists gwml2_gwwell_gw_well_unit_gwwell_id_30648c26
	on gwml2_gwwell_gw_well_unit (gwwell_id);

create index if not exists gwml2_gwwell_gw_well_unit_gwhydrogeounit_id_50cb2836
	on gwml2_gwwell_gw_well_unit (gwhydrogeounit_id);

create table if not exists gwml2_gwwell_gw_well_water_use
(
	id serial not null
		constraint gwml2_gwwell_gw_well_water_use_pkey
			primary key,
	gwwell_id integer not null
		constraint gwml2_gwwell_gw_well_gwwell_id_14bd35c9_fk_gwml2_gww
			references gwml2_gwwell
				deferrable initially deferred,
	wellwaterusetype_id integer not null
		constraint gwml2_gwwell_gw_well_wellwaterusetype_id_b889e3ea_fk_gwml2_wel
			references gwml2_wellwaterusetype
				deferrable initially deferred,
	constraint gwml2_gwwell_gw_well_wat_gwwell_id_wellwaterusety_88a90a37_uniq
		unique (gwwell_id, wellwaterusetype_id)
);

alter table gwml2_gwwell_gw_well_water_use owner to geonode;

create index if not exists gwml2_gwwell_gw_well_water_use_gwwell_id_14bd35c9
	on gwml2_gwwell_gw_well_water_use (gwwell_id);

create index if not exists gwml2_gwwell_gw_well_water_use_wellwaterusetype_id_b889e3ea
	on gwml2_gwwell_gw_well_water_use (wellwaterusetype_id)

end;
