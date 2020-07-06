create view groundwater_well as
SELECT gwml2_gwwell.id,
       gwml2_gwwell.gw_well_name         AS well_name,
       gwml2_gwwell.gw_well_total_length AS well_total_length,
       gwml2_gwwell.gw_well_location
FROM gwml2_gwwell;