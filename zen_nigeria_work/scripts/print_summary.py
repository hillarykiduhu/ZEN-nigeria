"""Print the key results of a ZEN-garden run so they can be pasted into a message.
Usage (zen-nigeria env, from the zen_nigeria_work folder):
    python scripts\\print_summary.py outputs\\nigeria_stage1_rice_husk
"""
import sys
from zen_garden import Results

path = sys.argv[1] if len(sys.argv) > 1 else "outputs/nigeria_stage1_rice_husk"
r = Results(path)
print("RUN:", path)

def show(title, name, cols=None):
    print("\n--", title, "(" + name + ")")
    try:
        df = r.get_total(name).reset_index()
        if cols:
            df = df[[c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]]
        print(df.round(4).to_string(index=False))
    except Exception as e:
        print("  not available:", type(e).__name__)

show("Cooking supply by technology, GWh", "flow_conversion_output")
show("Imports, GWh", "flow_import")
show("Capacity, GW", "capacity")
show("Capacity additions, GW", "capacity_addition")
show("Yearly capex, MUSD", "cost_capex_yearly")
show("Carrier cost, MUSD", "cost_carrier_total")
show("Net present cost, MUSD", "net_present_cost")
show("Total cost, MUSD", "cost_total")
