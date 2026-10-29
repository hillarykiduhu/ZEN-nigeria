"""Overview plots for a ZEN-garden 3.1.1 run (works for one year or many).
Usage (inside the zen-nigeria env, from the folder holding outputs/):
    python plot_results.py outputs\\nigeria_stage1_rice_husk
Writes results_overview.png and prints the underlying tables."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from zen_garden import Results

path = sys.argv[1] if len(sys.argv) > 1 else "outputs/nigeria_stage1_rice_husk"
r = Results(path)

def wide(name, index_cols):
    """Annual totals as a table: rows = index_cols, columns = model years."""
    df = r.get_total(name).reset_index()
    years = [c for c in df.columns if c not in ("node", "location", "capacity_type")
             and c not in index_cols and c != "set_years"]
    return df.groupby(index_cols)[years].sum()

supply = wide("flow_conversion_output", ["technology", "carrier"])   # GWh/yr
imports = wide("flow_import", ["carrier"])                           # GWh/yr
capacity = wide("capacity", ["technology"])                          # GW
cost = r.get_total("cost_total").reset_index().set_index("year")["cost_total"]  # megaUSD

for t in (supply, imports, capacity, cost):
    print(t.to_string(), "\n")

fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))

# 1) supply of the demand carrier by technology, stacked over years
demand_carrier = "cooking_service"            # change to "electricity", "transport_service"
s = supply.xs(demand_carrier, level="carrier").T
s.plot(kind="bar", stacked=True, ax=ax[0])
ax[0].set_title(f"{demand_carrier} supply by technology (GWh/yr)"); ax[0].set_xlabel("year")

# 2) imports by carrier: shows capped residues and the fossil fallback
imports[(imports > 0).any(axis=1)].T.plot(kind="bar", stacked=True, ax=ax[1])
ax[1].set_title("Imports by carrier (GWh/yr)"); ax[1].set_xlabel("year")

# 3) installed capacity
capacity.T.plot(kind="bar", ax=ax[2])
ax[2].set_title("Installed capacity (GW)"); ax[2].set_xlabel("year")

plt.tight_layout(); plt.savefig("results_overview.png", dpi=150)
print("saved results_overview.png")
