CREATE FUNCTION update_mv() RETURNS trigger AS
    $update_mv$
BEGIN
        refresh
materialized view mv_well_ggmn;
        refresh
materialized view mv_well;
RETURN NEW;
END;
    $update_mv$
LANGUAGE plpgsql;

CREATE TRIGGER trigger_well
    AFTER INSERT
    ON well
    FOR EACH ROW EXECUTE PROCEDURE update_mv();