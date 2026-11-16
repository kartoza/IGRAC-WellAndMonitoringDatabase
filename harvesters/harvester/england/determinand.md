# England Water Quality - Determinand mapping

Mapping EA Water Quality determinand to IGRAC parameter.

Source: https://environment.data.gov.uk/water-quality/codelist/determinand

| determinand | prefLabel                               | parameter_name_in_ggis       |
|-------------|-----------------------------------------|------------------------------|
| 0050        | Lead                                    | Pb (Lead)                    |
| 0061        | pH                                      | pH (Acidity)                 |
| 0062        | Conductivity at 20 C                    | EC (Electrical conductivity) |
| 0076        | Temperature of Water                    | T (Temperature)              |
| 0077        | Conductivity at 25 C                    | EC at 25°                    |
| 0099        | Carbon, Organic, Total as C :- {TOC}    | TOC (Total organic carbon)   |
| 0105        | Mercury                                 | Hg (Mercury)                 |
| 0108        | Cadmium                                 | Cd (Cadmium)                 |
| 0116        | Nitrogen, Total Oxidised as N           | Nitrate + nitrite            |
| 0138        | Solids, Total Dissolved at 180 C: {TDS} | TDS (Total dissolved solids) |
| 0158        | Hardness, Total as CaCO3                | Hardness                     |
| 0162        | Alkalinity to pH 4.5 as CaCO3           | TAC (Total alkalinity)       |
| 0171        | Bromide                                 | Br (Bromide)                 |
| 0172        | Chloride                                | Cl (Cloride)                 |
| 0177        | Fluoride                                | F (Fluoride)                 |
| 0180        | Orthophosphate, reactive as P           | P (orthophosphate)           |
| 0182        | Silica, reactive as SiO2                | SiO₂                         |
| 0183        | Sulphate as SO4                         | SO4 (Sulfate)                |
| 0193        | Carbonate as CO3                        | CO₃ (Carbonate ion)          |
| 0207        | Sodium                                  | Na (Sodium)                  |
| 0211        | Potassium                               | K (Potassium)                |
| 0237        | Magnesium                               | Mg (Magnesium)               |
| 0241        | Calcium                                 | Ca (Calcium)                 |
| 0912        | Chlorine : Total Available              | Cl₂ (Total chlorine)         |
| 1047        | Caesium                                 | Cs (Cesium)                  |
| 1089        | Rubidium                                | Rb (Rubidium)                |
| 1198        | Salinity                                | Salinity                     |
| 2331        | Coliforms, Total : Confirmed : MF       | Total coliforms              |
| 2347        | Escherichia coli : Confirmed : MF       | E Coli (Escherichia coli)    |
| 2550        | Streptococci : Faecal : Confirmed : MF  | FS (Fecal streptococci)      |
| 3164        | Chromium                                | Cr (Chromium)                |
| 3458        | Coliforms, Faecal : Confirmed           | FC (Fecal coliforms)         |
| 4370        | Chromium Hexavalent                     | Cr(VI) (Hexavalent chromium) |
| 6030        | Silver                                  | Ag (Silver)                  |
| 6040        | Tin                                     | Sn                           |
| 6045        | Arsenic, Dissolved                      | As (Soluble arsenic)         |
| 6049        | Selenium                                | Se (Selenium)                |
| 6054        | Cobalt                                  | Co (Kobalt)                  |
| 6057        | Aluminium                               | Al (Aluminium)               |
| 6058        | Antimony                                | Sb (Antimony)                |
| 6059        | Boron                                   | B (Boron)                    |
| 6060        | Titanium                                | Ti (Titanium)                |
| 6061        | Vanadium                                | V (Vanadium)                 |
| 6062        | Barium                                  | Ba (Barium)                  |
| 6063        | Strontium                               | Sr (Strontium)               |
| 6064        | Lithium                                 | Li (Lithium)                 |
| 6396        | Turbidity                               | Turbidity                    |
| 6452        | Copper                                  | Cu (Copper)                  |
| 6455        | Zinc                                    | Zn (Zinc)                    |
| 6458        | Manganese, Dissolved                    | Mn (Soluble manganese)       |
| 6460        | Iron, Dissolved                         | Fe (Soluble iron)            |
| 6462        | Nickel                                  | Ni (Nickel)                  |
| 6718        | Bismuth                                 | Bi (Bismut)                  |
| 6977        | Niobium, Dissolved                      | Nb (Niobium)                 |
| 6988        | Redox Potential                         | Eh (Redox potential)         |
| 7237        | Cerium                                  | Ce (Cerium)                  |
| 7362        | Zirconium                               | Zr (Zirconium)               |
| 9573        | Molybdenum                              | Mo (Molybdeen)               |
| 9584        | Bicarbonate as HCO3                     | HCO₃ (Bicarbonate)           |
| 9686        | Nitrogen, Total as N                    | Total nitrogen               |
| 9696        | Beryllium                               | Be (Beryllium)               |
| 9809        | Uranium, Dissolved                      | U (Soluble uranium)          |
| 9901        | Oxygen, Dissolved, % Saturation         | Oxygen saturation rate       |
| 9924        | Oxygen, Dissolved as O2                 | DO (Dissolved Oxygen)        |

## Need conversion

EA reports these determinands as N. The value must be multiplied by `factor` to get the IGRAC parameter (as ion).

| determinand | prefLabel                | parameter_name_in_ggis | from | to  | factor |
|-------------|--------------------------|------------------------|------|-----|--------|
| 0111        | Ammoniacal Nitrogen as N | NH₄ (Ammonium)         | N    | NH4 | 1.288  |
| 0117        | Nitrate as N             | NO3 (Nitrate)          | N    | NO3 | 4.427  |
| 0118        | Nitrite as N             | NO₂ (Nitrite)          | N    | NO2 | 3.285  |
