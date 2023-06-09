CREATE SCHEMA IF NOT EXISTS istsos;

-- PROCEDURES --
CREATE VIEW istsos.procedures AS
SELECT w.id                     as id_prc,
       ''                       as assignedid_prc,
       w.original_id            as name_prc,
       w.description            as desc_prc,
       w.first_time_measurement as stime_prc,
       w.last_time_measurement  as etime_prc,
       null                     as time_res_prc,
       null                     as time_acq_prc,
       1                        as id_oty_fk,
       w.id                     as id_foi_fk,
       ''                       as mqtt_prc
from vw_well as w;

-- OBS_TYPE --
CREATE TABLE istsos.obs_type
(
    id_oty   integer,
    name_oty varchar(64) UNIQUE,
    desc_oty text
);
INSERT INTO istsos.obs_type(id_oty, name_oty, desc_oty)
VALUES (1, 'insitu-fixed-point', '');

-- OBSERVED_PROPERTIES --
CREATE VIEW istsos.observed_properties AS
SELECT p.id          as id_opr,
       p.name        as name_opr,
       concat(
               'urn:ogc:def:parameter:x-igrac:1.0:', g.name, ':',
               p.name
           )         as def_opr,
       p.description as desc_opr,
       u.id          as unit_id,
       u.name        as unit_name,
       u.description as unit_description,
       ''            as constr_opr
from term_measurement_parameter as p
         LEFT JOIN term_measurement_parameter_group_parameters as r
                   ON r.termmeasurementparameter_id = p.id
         LEFT JOIN term_measurement_parameter_group as g
                   ON r.termmeasurementparametergroup_id = g.id
         LEFT JOIN unit as u ON u.id = p.default_unit_id;

-- UOMS --
CREATE VIEW istsos.uoms AS
SELECT unit_name        as name_uom,
       unit_description as desc_uom,
       unit_id          as id_uom
from istsos.observed_properties
WHERE unit_id IS NOT NULL
GROUP BY unit_id, unit_name, unit_description;

-- PROC_OBS --
CREATE VIEW istsos.proc_obs AS
SELECT concat(opr.id_opr, '-', opr.unit_id, '-', proc.id_prc) as id_pro,
       opr.id_opr                                             as id_opr_fk,
       opr.unit_id                                            as id_uom_fk,
       proc.id_prc                                            as id_prc_fk,
       ''                                                     as constr_pro
from istsos.observed_properties as opr
         CROSS JOIN istsos.procedures as proc;

-- OFFERINGS --
CREATE TABLE istsos.offerings
(
    name_off       varchar(64) UNIQUE,
    desc_off       text,
    expiration_off timestamptz,
    active_off     bool,
    id_off         integer
);
INSERT INTO istsos.offerings(name_off, desc_off, active_off, id_off)
VALUES ('measurement', 'measurement', True, 1);

-- OFF_PROC --
CREATE VIEW istsos.off_proc AS
SELECT id_prc as id_off_prc,
       id_prc as id_prc_fk,
       1      as id_off_fk
from istsos.procedures;

-- FEATURE_TYPE --
CREATE VIEW istsos.feature_type AS
SELECT name as name_fty,
       id   as id_fty
from term_feature_type;

-- FOI --
CREATE VIEW istsos.foi AS
SELECT w.description     as desc_foi,
       w.feature_type_id as id_fty_fk,
       w.id              as id_foi,
       w.name            as name_foi,
       ST_SetSRID(
               ST_MakePoint(
                       ST_X(w.location),
                       ST_Y(w.location),
                       w.altitiude
                   ),
               4326)
                         as geom_foi
from vw_well as w;

-- EVENT_TIME --
CREATE VIEW istsos.event_time AS
SELECT id      as id_eti,
       well_id as id_prc_fk,
       time    as time_eti
from vw_well_measurement;

-- MEASURES --
CREATE VIEW istsos.measures AS
SELECT id                                                       as id_msr,
       id                                                       as id_eti_fk,
       null                                                     as id_qi_fk,
       concat(parameter_id, '-', default_unit_id, '-', well_id) as id_pro_fk,
       default_value                                            as val_msr
from vw_well_measurement;

-- POSITIONS --
CREATE VIEW istsos.positions AS
SELECT w.id   as id_pos,
       null   as id_qi_fk,
       w.id   as id_foi,
       eti.id_eti as id_eti_fk,
       ST_SetSRID(
               ST_MakePoint(
                       ST_X(w.location),
                       ST_Y(w.location),
                       w.altitiude
                   ),
               4326)
              as geom_pos
from vw_well as w
         LEFT JOIN istsos.event_time eti ON eti.id_prc_fk = w.id;

-- TEMPORARY --
CREATE VIEW istsos.vw_istsos_sensor AS
SELECT well.id          as id,
       ST_X(location)   as longitude,
       ST_Y(location)   as latitude,
       ground.value     as elevation_value,
       unit.name        as elevation_unit,
       well.original_id as original_id,
       well.ggis_uid    as ggis_uid,
       well.name        as name
from well
         LEFT JOIN quantity ground
                   on ground.id = well.ground_surface_elevation_id
         LEFT JOIN unit on unit.id = ground.unit_id;