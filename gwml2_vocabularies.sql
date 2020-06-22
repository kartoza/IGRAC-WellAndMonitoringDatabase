INSERT INTO groundwater.CI_OnlineFunctionTerm (name) VALUES  ('download'), ('information'), ('offlineAccess'), ('order'), ('search');
INSERT INTO groundwater.CI_RoleTerm (name) VALUES ('resourceProvide'), ('custodian'), ('owner'), ('user'), ('distributor'), ('originator'), ('pointOfContact'), ('principalInvestigator'), ('processor'), ('publisher'), ('author');
INSERT INTO groundwater.BoreholeStartPointTypeTerm (name) VALUES ('natural ground surface'), ('open pit floor or wall'), ('underground'), ('from pre-existing hole');
INSERT INTO groundwater.BoreholeInclinationTerm (name) VALUES ('vertical'), ('horizontal'), ('inclined up'), ('inclined down');


INSERT INTO groundwater.BoreholeDrillingMethodTerm (prefix, p_name, uri, term_e)
VALUES
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/AirRotaryDrilling', 'Air rotary drilling'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Auger', 'Auger'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Backhoe', 'Backhoe'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Bored', 'Bored'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/CableToolDrilling', 'Cable tool drilling'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Combinaition', 'Combination'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/DiamondDrilling', 'Diamond Drilling'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/DownholeHammer', 'Downhole hammer'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Drilled', 'Drilles'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Driven', 'Driven'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Dug', 'Dug'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Dugout', 'Dugout'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Excavator', 'Excavator'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Hammer', 'Hammer'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/HandDug', 'Hand Dug'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Jetted', 'Jetted'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/MudRotaryDrilling', 'Mud rotary drllling'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Other', 'Other'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Push', 'Pushed'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/RotaryDrilling', 'Rotary Drilling'),
('gwml2c', 'bholeDrillingMethod', 'http://www.opengis.net/def/gwml/procedure/Sonic', 'Sonic');