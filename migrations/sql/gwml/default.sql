DROP MATERIALIZED VIEW IF EXISTS mv_well_ggmn;
DROP MATERIALIZED VIEW IF EXISTS mv_well;
DROP VIEW IF EXISTS view_well;

DROP TRIGGER IF EXISTS trigger_country ON country;
DROP TRIGGER IF EXISTS trigger_organisation ON organisation;
DROP TRIGGER IF EXISTS trigger_well ON well;
DROP FUNCTION IF EXISTS update_mv();