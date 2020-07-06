-- GW FLOW --
-- AquiferTypeTerm --
INSERT INTO public.gwml2_aquifertypeterm (name, description) VALUES ('unconfined', '');
INSERT INTO public.gwml2_aquifertypeterm (name, description) VALUES ('confined', '');
INSERT INTO public.gwml2_aquifertypeterm (name, description) VALUES ('artesian', '');
INSERT INTO public.gwml2_aquifertypeterm (name, description) VALUES ('subartesian', '');
INSERT INTO public.gwml2_aquifertypeterm (name, description) VALUES ('aquitard', '');

-- SpatialConfinementTypeTerm --
INSERT INTO public.gwml2_spatialconfinementtypeterm (name, description) VALUES ('Unconfined-Confined', '');
INSERT INTO public.gwml2_spatialconfinementtypeterm (name, description) VALUES ('Partially Confined', '');

-- ConductivityConfinementTypeTerm --
INSERT INTO public.gwml2_conductivityconfinementtypeterm (name, description) VALUES ('aquiclude', '');

-- PorosityTypeTerm --
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('primary', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('secondary', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('dual', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('specific', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('effective', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('granular', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('fractured', '');
INSERT INTO public.gwml2_porositytypeterm (name, description) VALUES ('karstic', '');