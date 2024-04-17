DROP MATERIALIZED VIEW IF EXISTS mv_well_ggmn;
DROP MATERIALIZED VIEW IF EXISTS mv_well;
DROP MATERIALIZED VIEW IF EXISTS mv_well_measurement;
DROP VIEW IF EXISTS vw_well_measurement;
DROP VIEW IF EXISTS vw_well;

DROP TRIGGER IF EXISTS trigger_organisation ON organisation;
DROP TRIGGER IF EXISTS trigger_user_uuid ON user_uuid;
DROP TRIGGER IF EXISTS trigger_well ON well;
DROP FUNCTION IF EXISTS update_mv();