CREATE TYPE groundwater.CI_OnLineFunctionTerm AS ENUM ('download', 'information', 'offlineAccess', 'order', 'search');

CREATE TYPE groundwater.CI_RoleTerm AS ENUM ('resourceProvide', 'custodian', 'owner', 'user', 'distributor', 'originator', 'pointOfContact', 'principalInvestigator', 'processor', 'publisher', 'author');

CREATE TYPE groundwater.BoreholeDrillingMethodTerm AS ENUM ('auger', 'hand auger', 'air core', 'cable tool', 'diamond core', 'direct push', 'hydraulic rotary', 'RAB', 'RC', 'vibratory');

CREATE TYPE groundwater.BoreholeStartPointTypeTerm AS ENUM ('natural ground surface', 'open pit floor or wall', 'underground', 'from pre-existing hole');

CREATE TYPE groundwater.BoreholeInclinationTerm AS ENUM ('vertical', 'horizontal', 'inclined up', 'inclined down');

COMMENT ON TYPE groundwater.BoreholeInclinationTerm IS 'Type of borehole inclination, e.g. vertical or horizontal.';
COMMENT ON TYPE groundwater.BoreholeDrillingMethodTerm IS 'Method of drilling., e.g. auger: http://en.wikipedia.org/wiki/Drilling_rig#Auger_drilling; air core: http://en.wikipedia.org/wiki/Drilling_rig#Air_core_drilling; cable tool: 	http://en.wikipedia.org/wiki/Drilling_rig#Cable_tool_drilling; diamond core: http://en.wikipedia.org/wiki/Drilling_rig#Diamond_core_drilling; direct push: http://en.wikipedia.org/wiki/Drilling_rig#Direct_Push_Rigs; hydraulic rotary: 	http://en.wikipedia.org/wiki/Drilling_rig#Hydraulic-rotary_drilling; RAB: http://en.wikipedia.org/wiki/Drilling_rig#Percussion_rotary_air_blast_drilling; RC: http://en.wikipedia.org/wiki/Drilling_rig#Reverse_circulation; vibratory: http://en.wikipedia.org/wiki/Drilling_rig#Sonic_%28Vibratory%29_Drilling';

