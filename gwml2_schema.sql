CREATE SCHEMA groundwater;

CREATE TABLE groundwater.borehole (
	id serial PRIMARY KEY,
	bholeDateOfDrilling DATE,
	bholeDriller VARCHAR (255),
	bholeDrillingMethod VARCHAR (255),
	bholeInclinationType VARCHAR (255),
	bholeMaterialCustodian VARCHAR (255),
	bholeNominalDiameter float(8),
	bholeOperator VARCHAR (255),
	bholeStartPoint VARCHAR (255),
	bholeCoreInterval GEOMETRY
);

CREATE TABLE groundwater.borecollar (
  id serial PRIMARY KEY,
  collarElevation float(8),
  collarElevationType VARCHAR (255),
  collarHeadworkType VARCHAR (255),
  collarLocation geometry(POINT,4326),
  bholeHeadworks int4 REFERENCES groundwater.borehole(id) ON DELETE CASCADE
);

COMMENT ON SCHEMA groundwater IS 'GWML2 Schema.';
COMMENT ON COLUMN groundwater.borehole.id IS 'Borehole ID.';
COMMENT ON COLUMN groundwater.borehole.bholeDateOfDrilling IS 'Date of drilling.';
COMMENT ON COLUMN groundwater.borehole.bholeDriller IS 'The organisation responsible for drilling the borehole (as opposed to commissioning the borehole).';
COMMENT ON COLUMN groundwater.borehole.bholeDrillingMethod IS 'Method of drilling.';
COMMENT ON COLUMN groundwater.borehole.bholeInclinationType IS 'Type of borehole inclination, e.g. vertical or horizontal.';
COMMENT ON COLUMN groundwater.borehole.bholeMaterialCustodian IS 'Method of drilling.';
COMMENT ON COLUMN groundwater.borehole.bholeNominalDiameter IS 'Diameter of the borehole.';
COMMENT ON COLUMN groundwater.borehole.bholeOperator IS 'Organisation responsible for commissioning the borehole (as opposed to drilling the borehole).';
COMMENT ON COLUMN groundwater.borehole.bholeStartPoint IS 'Describes the location of the start of the borehole, e.g. ground surface.';
COMMENT ON COLUMN groundwater.borehole.bholeCoreInterval IS 'The geometries for the intervals from which core is extracted along the borehole.';

COMMENT ON COLUMN groundwater.borecollar.id IS 'Borecollar ID.';
COMMENT ON COLUMN groundwater.borecollar.collarElevation IS 'The elevation of the bore collar with CRS and UOM.';
COMMENT ON COLUMN groundwater.borecollar.collarElevationType IS 'Type of reference elevation, defined as a feature, e.g. Top of Casing, Ground, etc.';
COMMENT ON COLUMN groundwater.borecollar.collarHeadworkType IS 'Type of assembly bolted to the production casing to control the well, and to provide access and protection (e.g. from flooding, vandalism). Example: raised tube, covers, manhole, ''Gattick Cover'' flush, concrete ring, etc. (after Fretwell, et al., 2006).';
COMMENT ON COLUMN groundwater.borecollar.collarLocation IS 'The geographical location of the collar.';
