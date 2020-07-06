-- GW Fluid Body --
-- StateType --
INSERT INTO public.gwml2_statetype (name, description) VALUES ('Solid', '');
INSERT INTO public.gwml2_statetype (name, description) VALUES ('Liquid', '');
INSERT INTO public.gwml2_statetype (name, description) VALUES ('Gas', '');

-- MaterialType --
INSERT INTO public.gwml2_materialtype (name, description) VALUES ('Sediment', '');

-- ChemicalType --
INSERT INTO public.gwml2_chemicaltype (name, description) VALUES ('Arsenic', '');

-- ConstituentRelationType --
INSERT INTO public.gwml2_constituentrelationtype (name, description) VALUES ('Coating', '');
INSERT INTO public.gwml2_constituentrelationtype (name, description) VALUES ('Constitution', '');
INSERT INTO public.gwml2_constituentrelationtype (name, description) VALUES ('Aggregation', '');
INSERT INTO public.gwml2_constituentrelationtype (name, description) VALUES ('Containment', '');

-- MechanismType --
INSERT INTO public.gwml2_mechanismtype (name, description) VALUES ('Sorption', '');
INSERT INTO public.gwml2_mechanismtype (name, description) VALUES ('Precipitation', '');
INSERT INTO public.gwml2_mechanismtype (name, description) VALUES ('Digestion', '');
INSERT INTO public.gwml2_mechanismtype (name, description) VALUES ('Excretion', '');

-- BodyQualityType --
INSERT INTO public.gwml2_bodyqualitytype (name, description) VALUES ('Saline', '');
INSERT INTO public.gwml2_bodyqualitytype (name, description) VALUES ('Brackish', '');
INSERT INTO public.gwml2_bodyqualitytype (name, description) VALUES ('Fresh', '');
INSERT INTO public.gwml2_bodyqualitytype (name, description) VALUES ('Turbide', '');
INSERT INTO public.gwml2_bodyqualitytype (name, description) VALUES ('Sulfurous', '');
INSERT INTO public.gwml2_bodyqualitytype (name, description) VALUES ('Mixed', '');

-- GWBodyPropertyType --
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Age', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Temperature', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Density', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Viscosity', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Turbidity', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Color', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Hardness', '');
INSERT INTO public.gwml2_gwbodypropertytype (name, description) VALUES ('Acidity', '');

-- SurfaceType --
INSERT INTO public.gwml2_surfacetype (name, description) VALUES ('Piezometric', '');
INSERT INTO public.gwml2_surfacetype (name, description) VALUES ('Potentiometric', '');
INSERT INTO public.gwml2_surfacetype (name, description) VALUES ('Water Table', '');
INSERT INTO public.gwml2_surfacetype (name, description) VALUES ('Salt Wedge', '');

-- MixtureType --
INSERT INTO public.gwml2_mixturetype (name, description) VALUES ('Solution', '');
INSERT INTO public.gwml2_mixturetype (name, description) VALUES ('Suspension', '');
INSERT INTO public.gwml2_mixturetype (name, description) VALUES ('Emulsion', '');
INSERT INTO public.gwml2_mixturetype (name, description) VALUES ('Precipitate', '');
INSERT INTO public.gwml2_mixturetype (name, description) VALUES ('Colloidal', '');

-- YieldType --
INSERT INTO public.gwml2_yieldtype (name, description) VALUES ('Specific Yield', '');
INSERT INTO public.gwml2_yieldtype (name, description) VALUES ('Safe Yield', '');
