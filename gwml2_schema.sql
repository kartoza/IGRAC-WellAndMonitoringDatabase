CREATE SCHEMA groundwater;

CREATE TABLE groundwater.CI_Telephone (
	id serial PRIMARY KEY,
	voice VARCHAR(50),
	facsimile VARCHAR(50)

);

CREATE TABLE groundwater.CI_Address (
	id serial PRIMARY KEY,
	deliveryPoint VARCHAR(50),
	city VARCHAR(150),
	administrativeArea VARCHAR(150),
	postalCode VARCHAR(50),
	country VARCHAR(150),
	electronicMailAddress VARCHAR(150)
);

CREATE TYPE groundwater.CI_OnLineFunctionTerm AS ENUM ('download', 'information', 'offlineAccess', 'order', 'search');

CREATE TABLE groundwater.CI_OnlineResource (
	id serial PRIMARY KEY,
	linkage VARCHAR(150),
	protocol VARCHAR(150),
	applicationProfile VARCHAR(250),
	name VARCHAR(150),
	description VARCHAR(255),
	function groundwater.CI_OnLineFunctionTerm
);

CREATE TABLE groundwater.CI_Contact (
	id serial PRIMARY KEY,
	phone int4 REFERENCES groundwater.CI_Telephone(id) ON DELETE SET NULL,
	address int4 REFERENCES groundwater.CI_Address(id) ON DELETE SET NULL,
	onlineResource int4 REFERENCES groundwater.CI_OnlineResource(id) ON DELETE SET NULL,
	hoursOfService VARCHAR (255),
	contactInstructions VARCHAR (255)
);

CREATE TYPE groundwater.CI_RoleTerm AS ENUM ('resourceProvide', 'custodian', 'owner', 'user', 'distributor', 'originator', 'pointOfContact', 'principalInvestigator', 'processor', 'publisher', 'author');

CREATE TABLE groundwater.CI_ResponsibleParty (
	id serial PRIMARY KEY,
	individualName VARCHAR (255),
	organisationName VARCHAR (255),
	positionName VARCHAR (255),
	contactInfo int4 REFERENCES groundwater.CI_Contact(id) ON DELETE SET NULL,
	role groundwater.CI_RoleTerm
);

CREATE TYPE groundwater.BoreholeDrillingMethodTerm AS ENUM ('auger', 'hand auger', 'air core', 'cable tool', 'diamond core', 'direct push', 'hydraulic rotary', 'RAB', 'RC', 'vibratory');

CREATE TYPE groundwater.BoreholeStartPointTypeTerm AS ENUM ('natural ground surface', 'open pit floor or wall', 'underground', 'from pre-existing hole');

CREATE TYPE groundwater.BoreholeInclinationTerm AS ENUM ('vertical', 'horizontal', 'inclined up', 'inclined down');

CREATE TABLE groundwater.GM_Envelope (
	id serial PRIMARY KEY,
	upperCorner GEOMETRY,
	lowerCorner GEOMETRY
);

CREATE TABLE groundwater.borehole (
	id serial PRIMARY KEY,
	bholeDateOfDrilling DATE,
	bholeInclinationType groundwater.BoreholeInclinationTerm,
	bholeMaterialCustodian int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON DELETE SET NULL,
	bholeNominalDiameter float(8),
	bholeOperator int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON DELETE SET NULL,
	bholeStartPoint groundwater.BoreholeStartPointTypeTerm
);

CREATE TABLE groundwater.borehole_bholeCoreInterval (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeCoreInterval int4 REFERENCES groundwater.GM_Envelope(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borehole_bholeDriller (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeDriller int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borehole_bholeDrillingMethod (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeDrillingMethod groundwater.BoreholeDrillingMethodTerm
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

COMMENT ON COLUMN groundwater.borehole.bholeInclinationType IS 'Type of borehole inclination, e.g. vertical or horizontal.';
COMMENT ON COLUMN groundwater.borehole.bholeMaterialCustodian IS 'Method of drilling.';
COMMENT ON COLUMN groundwater.borehole.bholeNominalDiameter IS 'Diameter of the borehole.';
COMMENT ON COLUMN groundwater.borehole.bholeOperator IS 'Organisation responsible for commissioning the borehole (as opposed to drilling the borehole).';
COMMENT ON COLUMN groundwater.borehole.bholeStartPoint IS 'Describes the location of the start of the borehole, e.g. ground surface.';


COMMENT ON COLUMN groundwater.borecollar.id IS 'Borecollar ID.';
COMMENT ON COLUMN groundwater.borecollar.collarElevation IS 'The elevation of the bore collar with CRS and UOM.';
COMMENT ON COLUMN groundwater.borecollar.collarElevationType IS 'Type of reference elevation, defined as a feature, e.g. Top of Casing, Ground, etc.';
COMMENT ON COLUMN groundwater.borecollar.collarHeadworkType IS 'Type of assembly bolted to the production casing to control the well, and to provide access and protection (e.g. from flooding, vandalism). Example: raised tube, covers, manhole, ''Gattick Cover'' flush, concrete ring, etc. (after Fretwell, et al., 2006).';
COMMENT ON COLUMN groundwater.borecollar.collarLocation IS 'The geographical location of the collar.';
