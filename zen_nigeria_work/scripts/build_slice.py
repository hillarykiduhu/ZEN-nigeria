"""Currency: USD (price year still to be fixed, see docs/decisions.md). Reference year 2025.
Builds the stage-1 ZEN-Nigeria slice (Route A) from the 3.1.1 1_base_case templates.
Chain: processing_residue (rice husk, capped) -> collect_processing_residue -> solid_biomass
       -> improved_stove_biomass -> cooking_service  <-  lpg_stove <- lpg (import fallback)
Every number marked PLACEHOLDER is a structural test value, NOT a sourced parameter."""
import copy, shutil, sys
from pathlib import Path
import yaml

TPL = Path(sys.argv[1])               # .../1_base_case
SCEN = sys.argv[3] if len(sys.argv) > 3 else "central"   # optional: "upper" -> cooking demand option C2
OUT = Path(sys.argv[2]) / ("nigeria_stage1_rice_husk" + ("" if SCEN == "central" else "_" + SCEN))   # argv[2] = datasets folder
if OUT.exists(): shutil.rmtree(OUT)
def load(p): return yaml.safe_load(open(TPL / p))
def usd(text):  # template is in Euro; project currency is USD
    return text.replace("megaEuro", "megaUSD").replace("kiloEuro", "kiloUSD").replace("Euro", "USD")
def dump(d, p):
    p = OUT / p; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(usd(yaml.safe_dump(d, sort_keys=False)))

# ---------- placeholders (replace from ZEN_Nigeria_Data_Register.xlsx) ----------
P = dict(
    demand_cooking_GW=6.0256,         # CENTRAL (option A, Ibitoye 2013): 800 MJ/cap/yr x 237,527,782 /3.6/8760. See register
    husk_cap_GWh=3007.8,  # H2 with U = 25% of R: 9,129,900 t x 0.26 x 0.4 x 0.75 x 15.205 MJ/kg / 3600
    husk_price=0.8505,  # kUSD/GWh residue: Ghana husk logistics 2.64 USD/t (2014) x CPI 1.3606 / 4.2236 MWh/t
    lpg_price=71.55,  # kUSD/GWh: NBS 2025 12-mo mean 12.5kg refill / 12.5 / CBN 2025 avg 1517.09 NGN/USD x 76.11 (NCV 47.3 MJ/kg); register
    lpg_co2=0.22716,  # kilotons/GWh, IPCC 2006 63,100 kg/TJ
    collect_loss_factor=1.0,          # PLACEHOLDER GWh residue per GWh solid_biomass
    biomass_stove_input_per_out=4.7393,  # 1/0.211 improved husk stove (Nwakaire and Ugwuishiwu 2015); see register
    lpg_stove_input_per_out=2.0,      # PLACEHOLDER GWh LPG per GWh useful (eff 0.50)
    capex_collect=0.0, capex_biomass_stove=262.8,  # USD 30 / 0.1142 kW avg useful heat per household (Option 1); USD 2025, register P10
    life_biomass_stove=5.0, capex_lpg_stove=385.4,  # USD 44 / 0.1142 kW (Option 1); OnStove cost
    discount_rate=0.10,  # ESONE-Nigeria base case (Energy Environ. Sci. 2021, SI Note 3); sensitivity 5-15%; real/nominal not stated
    lpg_stove_share_hh=0.226,  # GHS-Panel W5 Table 3.6: LPG/natural gas stove as primary cookstove (alt. 0.232 = LPG used as cooking fuel, Table 3.8)
    lpg_stove_year_construction=2022,  # ASSUMPTION: mid-life vintage (7-year life, 3 years old in 2025)
    life_lpg_stove=7.0,  # OnStove default, paired with the USD 44 cost
)

if SCEN == "upper":
    P["demand_cooking_GW"] = 11.6593   # option C2 (register sheet Options_cooking_energy)

# ---------- energy_system ----------
for f in ["attributes.yaml", "base_units.yaml"]:
    d = load(f"energy_system/{f}")
    if f == "attributes.yaml":
        d["carbon_emissions_budget"]["default_value"] = "inf"   # no carbon cap in stage 1
        d["discount_rate"]["default_value"] = P["discount_rate"]
    dump(d, f"energy_system/{f}")
(OUT / "energy_system/unit_definitions.txt").write_text("USD = [currency]\n")
(OUT / "energy_system/set_nodes.csv").write_text("node,lon,lat\nNG,8.6753,9.0820\n")  # single national node
(OUT / "energy_system/set_edges.csv").write_text("edge,node_from,node_to\n")

# ---------- carriers ----------
carrier_tpl = load("set_carriers/natural_gas/attributes.yaml")
def carrier(name, demand=0.0, imp=0.0, imp_yearly="inf", price=0.0, co2=0.0, shed="inf"):
    d = copy.deepcopy(carrier_tpl)
    d["demand"]["default_value"] = demand
    d["availability_import"]["default_value"] = "inf" if imp == "inf" else imp
    d["availability_import_yearly"]["default_value"] = imp_yearly
    d["price_import"]["default_value"] = price
    d["carbon_intensity_carrier_import"]["default_value"] = co2
    d["carbon_intensity_carrier_export"]["default_value"] = co2
    d["price_shed_demand"]["default_value"] = shed
    dump(d, f"set_carriers/{name}/attributes.yaml")

carrier("processing_residue", imp="inf", imp_yearly=P["husk_cap_GWh"], price=P["husk_price"])
carrier("solid_biomass")
carrier("lpg", imp="inf", price=P["lpg_price"], co2=P["lpg_co2"])
carrier("cooking_service", demand=P["demand_cooking_GW"])

# ---------- conversion technologies ----------
tech_tpl = load("set_technologies/set_conversion_technologies/natural_gas_boiler/attributes.yaml")
def tech(name, inp, out, factor, capex, life=15.0):
    d = copy.deepcopy(tech_tpl)
    d["reference_carrier"]["default_value"] = [out]
    d["input_carrier"]["default_value"] = [inp]
    d["output_carrier"]["default_value"] = [out]
    d["conversion_factor"] = {inp: {"default_value": factor, "unit": "GWh/GWh"}}
    d["capex_specific_conversion"]["default_value"] = capex
    d["opex_specific_fixed"]["default_value"] = 0.0
    d["lifetime"]["default_value"] = life           # years (15 = PLACEHOLDER unless set)
    dump(d, f"set_technologies/set_conversion_technologies/{name}/attributes.yaml")

tech("collect_processing_residue", "processing_residue", "solid_biomass", P["collect_loss_factor"], P["capex_collect"])
tech("improved_stove_biomass", "solid_biomass", "cooking_service", P["biomass_stove_input_per_out"], P["capex_biomass_stove"], P["life_biomass_stove"])
tech("lpg_stove", "lpg", "cooking_service", P["lpg_stove_input_per_out"], P["capex_lpg_stove"], P["life_lpg_stove"])

# empty but required folders (ZEN-garden resolves every technology subset folder)
for sub in ["set_storage_technologies", "set_transport_technologies"]:
    d = OUT / "set_technologies" / sub; d.mkdir(parents=True, exist_ok=True); (d / ".gitkeep").write_text("")

# ---------- system ----------
s = load("system.yaml")
s["set_conversion_technologies"] = ["collect_processing_residue", "improved_stove_biomass", "lpg_stove"]
s["set_storage_technologies"] = []
s["set_transport_technologies"] = []
s["set_nodes"] = ["NG"]
s["reference_year"] = 2025
# one model year = 8760 hourly steps (constant profiles for now). With 1 step/year ZEN-garden
# treats the year as ONE HOUR, which makes GW demand and GWh yearly caps inconsistent.
s["unaggregated_time_steps_per_year"] = 8760
s["aggregated_time_steps_per_year"] = 8760
s["conduct_time_series_aggregation"] = False       # decided: 2025
dump(s, "system.yaml")
print("written", OUT)

# ---------- existing capacity (Option 1: GW of average useful heat = households x 1000 kWh/8760 h) ----------
_hh = 237.5277e6 / 4.5
_gw_per_hh = 1000.0 / 8760.0 / 1e6      # kW -> GW
_lpg_gw = round(_hh * P["lpg_stove_share_hh"] * _gw_per_hh, 4)
_f = OUT / "set_technologies/set_conversion_technologies/lpg_stove/capacity_existing.csv"
_f.write_text(f"node,capacity_existing,year_construction\nNG,{_lpg_gw},{P['lpg_stove_year_construction']}\n")
print("existing LPG stove capacity GW:", _lpg_gw)
