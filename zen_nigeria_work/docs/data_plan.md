# Stage-1 data plan (rice husk to stove, LPG fallback)

Order matters: each step unlocks a real check of the model against a number you can verify.

1. Cooking demand (GW)  households x useful energy per household. DHS 2018, NBS 2024, UN WPP 2024.
2. LPG: delivered price (NBS Price Watch, NMDPRA), LHV, CO2 factor (IPCC 2006), stove efficiency, stock.
3. Rice husk cascade (register sheet Cascade_rice_husk): P, rho, kappa, U, h.  U is the weak link.
4. Improved biomass stove: efficiency, cost per stove, lifetime, stock.
5. Collection technology: handling loss and cost (expect no Nigerian data: scenario range).
6. Decide price year and discount rate (register sheet Decisions).

Check after each fill: rebuild, solve, compare the husk share of cooking with the DHS share of
households using biomass for cooking. Large mismatch means a unit or ratio error.
