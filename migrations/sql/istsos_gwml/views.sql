CREATE VIEW vw_well AS
select w.id,
       w.description,
       w.number_of_measurements         as "number_of_measurements",
       w.number_of_measurements_level   as "number_of_measurements_level",
       w.number_of_measurements_quality as "number_of_measurements_quality",
       w.number_of_measurements_yield   as "number_of_measurements_yield",
       w.ggis_uid                       as "ggis_uid",
       w.original_id                    as "original_id",
       w.name                           as "name",
       type.name                        as "feature_type",
       type.id                          as "feature_type_id",
       purpose.name                     as "purpose",
       purpose.id                       as "purpose_id",
       status.name                      as "status",
       org.name                         as "organisation",
       org.id                           as "organisation_id",
       c.name                           as "country",
       drill.year_of_drilling           as "year_of_drilling",
       hp.aquifer_name                  as "aquifer_name",
       aquifer.name                     as "aquifer_type",
       mg.manager                       as "manager",
       w.location,
       w.created_at                     as "created_at",
       created_by.username              as "created_by",
       w.last_edited_at                 as "last_edited_at",
       last_edited_by.username          as "last_edited_by",
       q.value                          as "altitiude",
       u.name                           as "altitiude_unit",
       w.first_time_measurement,
       w.last_time_measurement,
       w.is_groundwater_level,
       w.is_groundwater_quality,
       concat('<a href="/groundwater/record/', w.id,
              '">Full Data Record</a>') as detail
from well as w
         LEFT JOIN organisation org on w.organisation_id = org.id
         LEFT JOIN country c on w.country_id = c.id
         LEFT JOIN term_feature_type type on w.feature_type_id = type.id
         LEFT JOIN term_well_purpose purpose on w.purpose_id = purpose.id
         LEFT JOIN term_well_status status on w.status_id = status.id
         LEFT JOIN drilling drill on w.drilling_id = drill.id
         LEFT JOIN hydrogeology_parameter hp
                   on w.hydrogeology_parameter_id = hp.id
         LEFT JOIN term_aquifer_type aquifer on hp.aquifer_type_id = aquifer.id
         LEFT JOIN management mg on w.management_id = mg.id
         LEFT JOIN user_uuid created_by ON w.created_by = created_by.user_id
         LEFT JOIN user_uuid last_edited_by
                   ON w.last_edited_by = last_edited_by.user_id
         LEFT JOIN quantity q ON q.id = w.id
         LEFT JOIN unit u ON u.id = q.unit_id
WHERE org.active = True;

-- WELL FOR ISTSOS MEASUREMENT --
CREATE VIEW vw_well_measurement AS
select id,
        time, well_id, default_unit_id, default_value, parameter_id
        from (
        SELECT id, time, well_id, default_unit_id, default_value, parameter_id
        from well_level_measurement where default_value IS NOT NULL
        UNION
        SELECT id, time, well_id, default_unit_id, default_value, parameter_id
        from well_quality_measurement where default_value IS NOT NULL
        UNION
        SELECT id, time, well_id, default_unit_id, default_value, parameter_id
        from well_yield_measurement where default_value IS NOT NULL
        ) as measurement;

-- MATERIALIZED VIEW FOR ISTSOS MEASUREMENT --
-- SCHEDULED REFRESH --
CREATE
MATERIALIZED VIEW mv_well_measurement AS
select *, concat(parameter_id, '-', default_unit_id, '-', well_id) as unique_fk
FROM vw_well_measurement;