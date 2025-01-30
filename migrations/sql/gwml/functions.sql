CREATE FUNCTION update_mv() RETURNS trigger AS
    $update_mv$
BEGIN
        refresh materialized view mv_well_ggmn;
        refresh materialized view mv_well;
    RETURN NEW;
RETURN NEW;
END;
    $update_mv$
LANGUAGE plpgsql;

CREATE TRIGGER trigger_well
    AFTER INSERT OR UPDATE OF last_edited_at
    ON well
    FOR EACH ROW EXECUTE PROCEDURE update_mv();

CREATE TRIGGER trigger_organisation
    AFTER UPDATE OF name
    ON organisation
    FOR EACH ROW EXECUTE PROCEDURE update_mv();

CREATE TRIGGER trigger_country
    AFTER UPDATE OF name
    ON country
    FOR EACH ROW EXECUTE PROCEDURE update_mv();