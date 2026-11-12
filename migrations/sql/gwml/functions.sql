CREATE FUNCTION update_mv() RETURNS trigger AS
    $update_mv$
BEGIN
        refresh materialized view mv_well;
    RETURN NEW;
RETURN NEW;
END;
    $update_mv$
LANGUAGE plpgsql;