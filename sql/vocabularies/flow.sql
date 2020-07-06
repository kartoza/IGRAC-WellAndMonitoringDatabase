-- GW FLOW --
-- WaterFlowProcess --
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('evapotranspiration', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('evaporation', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('transpiration', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('runoff', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('baseflow', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('pumping', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('infiltration', '');
INSERT INTO public.gwml2_waterflowprocess (name, description) VALUES ('injection', '');

-- TemporalType --
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('yearly', '');
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('monthly', '');
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('daily', '');
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('summer', '');
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('winter', '');
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('spring', '');
INSERT INTO public.gwml2_temporaltype (name, description) VALUES ('autumn', '');

-- FlowPersistenceType --
INSERT INTO public.gwml2_flowpersistencetype (name, description) VALUES ('ephemeral', '');
INSERT INTO public.gwml2_flowpersistencetype (name, description) VALUES ('intermittent', '');
INSERT INTO public.gwml2_flowpersistencetype (name, description) VALUES ('not specified', '');
INSERT INTO public.gwml2_flowpersistencetype (name, description) VALUES ('perennial', '');
INSERT INTO public.gwml2_flowpersistencetype (name, description) VALUES ('seasonal', '');