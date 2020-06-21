CREATE SCHEMA groundwater;

CREATE TABLE groundwater.Quantity (
	id serial PRIMARY KEY,
	unit VARCHAR (20),
	value float(8)
);

CREATE TABLE groundwater.CI_RoleTerm (
	id serial PRIMARY KEY,
	name VARCHAR (150)
);

CREATE TABLE groundwater.CI_Telephone (
	id serial PRIMARY KEY,
	voice VARCHAR (50),
	facsimile VARCHAR (50)
);

CREATE TABLE groundwater.CI_Address (
	id serial PRIMARY KEY,
	deliveryPoint VARCHAR (50),
	city VARCHAR (150),
	administrativeArea VARCHAR (150),
	postalCode VARCHAR (50),
	country VARCHAR (150),
	electronicMailAddress VARCHAR (150)
);

CREATE TABLE groundwater.CI_OnLineFunctionTerm (
	id serial PRIMARY KEY,
	name VARCHAR (150)
);

CREATE TABLE groundwater.CI_OnlineResource (
	id serial PRIMARY KEY,
	linkage VARCHAR(150),
	protocol VARCHAR(150),
	applicationProfile VARCHAR(250),
	name VARCHAR(150),
	description VARCHAR(255)
);

CREATE TABLE groundwater.CI_onlineresource_onlinefunctionterm (
	ci_onlineresource int4 REFERENCES groundwater.CI_OnlineResource(id) ON UPDATE CASCADE ON DELETE CASCADE,
	function int4 REFERENCES groundwater.CI_OnLineFunctionTerm(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.CI_Contact (
	id serial PRIMARY KEY,
	phone int4 REFERENCES groundwater.CI_Telephone(id) ON DELETE SET NULL,
	address int4 REFERENCES groundwater.CI_Address(id) ON DELETE SET NULL,
	onlineResource int4 REFERENCES groundwater.CI_OnlineResource(id) ON DELETE SET NULL,
	hoursOfService VARCHAR (255),
	contactInstructions VARCHAR (255)
);

CREATE TABLE groundwater.CI_ResponsibleParty (
	id serial PRIMARY KEY,
	individualName VARCHAR (255),
	organisationName VARCHAR (255),
	positionName VARCHAR (255),
	contactInfo int4 REFERENCES groundwater.CI_Contact(id) ON DELETE SET NULL
);

CREATE TABLE groundwater.ci_responsibleparty_roleterm (
	ci_responsibleparty int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON UPDATE CASCADE ON DELETE CASCADE,
	role int4 REFERENCES groundwater.CI_RoleTerm(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.GM_Envelope (
	id serial PRIMARY KEY,
	upperCorner geometry(POINT,4326),
	lowerCorner geometry(POINT,4326)
);

CREATE TABLE groundwater.BoreholeStartPointTypeTerm (
	id serial PRIMARY KEY,
	name VARCHAR (150)
);

CREATE TABLE groundwater.BoreholeInclinationTerm (
	id serial PRIMARY KEY,
	name VARCHAR (150)
);

CREATE TABLE groundwater.borehole (
	id serial PRIMARY KEY,
	bholeDateOfDrilling DATE,
	bholeNominalDiameter int4 REFERENCES groundwater.Quantity(id) ON DELETE SET NULL,
	bholeOperator int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON DELETE SET NULL
);

CREATE TABLE groundwater.borehole_bholeMaterialCustodian (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeMaterialCustodian int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borehole_bholeInclinationType (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeInclinationType int4 REFERENCES groundwater.BoreholeInclinationTerm(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borehole_bholeStartPoint (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeStartPoint int4 REFERENCES groundwater.BoreholeStartPointTypeTerm(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borehole_bholeCoreInterval (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeCoreInterval int4 REFERENCES groundwater.GM_Envelope(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borehole_bholeDriller (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeDriller int4 REFERENCES groundwater.CI_ResponsibleParty(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.BoreholeDrillingMethodTerm (
	id serial PRIMARY KEY,
	prefix VARCHAR (50),
	p_name VARCHAR (50),
	uri VARCHAR (255),
	term_e VARCHAR (150)
);

CREATE TABLE groundwater.borehole_bholeDrillingMethod (
	borehole int4 REFERENCES groundwater.borehole(id) ON UPDATE CASCADE ON DELETE CASCADE,
	bholeDrillingMethod int4 REFERENCES groundwater.BoreholeDrillingMethodTerm(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.borecollar (
  	id serial PRIMARY KEY,
  	collarElevation float(8),
  	collarElevationType VARCHAR (255),
  	collarHeadworkType VARCHAR (255),
  	collarLocation geometry(POINT,4326),
  	bholeHeadworks int4 REFERENCES groundwater.borehole(id) ON DELETE CASCADE
);

CREATE TABLE groundwater.Log_Value (
	id serial PRIMARY KEY,
	fromDepth int4 REFERENCES groundwater.Quantity(id) ON DELETE SET NULL,
	toDepth int4 REFERENCES groundwater.Quantity(id) ON DELETE SET NULL
);

CREATE TABLE groundwater.GW_GeologyLogCoverage (
	id serial PRIMARY KEY
);

CREATE TABLE groundwater.gw_geologylogcoverage_logvalue (
	gw_geologylogcoverage int4 REFERENCES groundwater.GW_GeologyLogCoverage(id) ON UPDATE CASCADE ON DELETE CASCADE,
	value int4 REFERENCES groundwater.Log_Value(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.GW_GeologyLog (
	id serial PRIMARY KEY,
	phenomenonTime timestamp,
	resultTime timestamp,
	parameter  VARCHAR (150),
	resultQuality int4 REFERENCES groundwater.GW_GeologyLogCoverage(id) ON DELETE SET NULL,
	startDepth int4 REFERENCES groundwater.Quantity(id) ON DELETE SET NULL,
	endDepth int4 REFERENCES groundwater.Quantity(id) ON DELETE SET NULL
);

CREATE TABLE groundwater.gw_geologylog_geologylogcoverage (
	gw_geologyLog int4 REFERENCES groundwater.GW_GeologyLog(id) ON UPDATE CASCADE ON DELETE CASCADE,
	result int4 REFERENCES groundwater.GW_GeologyLogCoverage(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.GW_HydrogeoUnit (
	id serial PRIMARY KEY
);

CREATE TABLE groundwater.GW_Well (
	id serial PRIMARY KEY,
	gwWellName VARCHAR(50),
	gwWellLocation geometry(POINT, 4326),
	gwWellContributionZone geometry(Polygon, 4326)
);

CREATE TABLE groundwater.gw_well_geology (
	gw_well int4 REFERENCES groundwater.GW_Well(id) ON UPDATE CASCADE ON DELETE CASCADE,
	gwWellGeology int4 REFERENCES groundwater.GW_GeologyLog(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE groundwater.gw_well_hydrogeounit (
	gw_well int4 REFERENCES groundwater.GW_Well(id) ON UPDATE CASCADE ON DELETE CASCADE,
	gwWellGeology int4 REFERENCES groundwater.GW_HydrogeoUnit(id) ON UPDATE CASCADE ON DELETE CASCADE
);

COMMENT ON SCHEMA groundwater IS 'GWML2 Schema.';
COMMENT ON COLUMN groundwater.borehole.id IS 'Borehole ID.';
COMMENT ON COLUMN groundwater.borehole.bholeDateOfDrilling IS 'Date of drilling.';

COMMENT ON TABLE groundwater.borehole_bholeInclinationType IS 'Type of borehole inclination, e.g. vertical or horizontal.';
COMMENT ON TABLE groundwater.borehole_bholeMaterialCustodian IS 'The custodian of the drill core or samples recovered from the borehole.';
COMMENT ON COLUMN groundwater.borehole.bholeNominalDiameter IS 'Diameter of the borehole.';
COMMENT ON COLUMN groundwater.borehole.bholeOperator IS 'Organisation responsible for commissioning the borehole (as opposed to drilling the borehole).';
COMMENT ON TABLE groundwater.borehole_bholeStartPoint IS 'Describes the location of the start of the borehole, e.g. ground surface.';

COMMENT ON COLUMN groundwater.borecollar.id IS 'Borecollar ID.';
COMMENT ON COLUMN groundwater.borecollar.collarElevation IS 'The elevation of the bore collar with CRS and UOM.';
COMMENT ON COLUMN groundwater.borecollar.collarElevationType IS 'Type of reference elevation, defined as a feature, e.g. Top of Casing, Ground, etc.';
COMMENT ON COLUMN groundwater.borecollar.collarHeadworkType IS 'Type of assembly bolted to the production casing to control the well, and to provide access and protection (e.g. from flooding, vandalism). Example: raised tube, covers, manhole, ''Gattick Cover'' flush, concrete ring, etc. (after Fretwell, et al., 2006).';
COMMENT ON COLUMN groundwater.borecollar.collarLocation IS 'The geographical location of the collar.';
