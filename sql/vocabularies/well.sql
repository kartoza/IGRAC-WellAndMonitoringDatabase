-- GW Well --
-- WellPurposeType --
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (1, 'Extraction', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (2, 'Injection', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (3, 'Observation', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (4, 'Dewatering', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (6, 'Decontamination', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (7, 'Disposal', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (9, 'Geotechnical', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (10, 'Mineral', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (12, 'Monitoring Quality', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (8, 'Flowing Shot', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (11, 'Monitoring Level Head', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (5, 'Cathodic Protection', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (13, 'Oil', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (14, 'Oil Exploratory', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (15, 'Seismic', '');
INSERT INTO public.gwml2_wellpurposetype (id, name, description) VALUES (16, 'Water Exploratory', '');

-- WellStatusTypeTerm --
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (1, 'New', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (2, 'Unfinished', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (3, 'Reconditioned', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (4, 'Deepened', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (5, 'Not in use', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (6, 'Standby', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (7, 'Unknown', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (8, 'Abandoned dry', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (9, 'Abandoned insufficient', '');
INSERT INTO public.gwml2_wellstatustypeterm (id, name, description) VALUES (10, 'Abandoned quality', '');

-- WellWaterUseType --
INSERT INTO public.gwml2_wellwaterusetype (id, name, description) VALUES (1, 'Agricultural', '');
INSERT INTO public.gwml2_wellwaterusetype (id, name, description) VALUES (2, 'Domestic', '');
INSERT INTO public.gwml2_wellwaterusetype (id, name, description) VALUES (3, 'Industrial', '');
INSERT INTO public.gwml2_wellwaterusetype (id, name, description) VALUES (4, 'Recreation', '');
