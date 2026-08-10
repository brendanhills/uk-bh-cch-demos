"""Generate the dummy Kmart supply-chain network (deterministic, fixed seed).

Purely fictional data: 3 distribution centres and 30 stores laid out in three
metro clusters on a 1000x760 plane (1 unit = 1 km), with weekly demand in
pallets. Run once to produce network.json.
"""
import json
import random
from pathlib import Path

rng = random.Random(42)

DCS = [
    {"id": "DC-SOUTH", "name": "Truganina DC", "x": 210, "y": 610},
    {"id": "DC-CENTRAL", "name": "Eastern Creek DC", "x": 620, "y": 380},
    {"id": "DC-NORTH", "name": "Larapinta DC", "x": 800, "y": 110},
]

CLUSTERS = [
    # (cx, cy, n_stores, spread)
    (230, 600, 11, 120),  # southern metro
    (630, 370, 11, 120),  # central metro
    (790, 120, 8, 100),   # northern metro
]

stores = []
i = 1
for cx, cy, n, spread in CLUSTERS:
    for _ in range(n):
        x = min(985, max(15, rng.gauss(cx, spread)))
        y = min(745, max(15, rng.gauss(cy, spread)))
        stores.append({
            "id": f"S{i:02d}",
            "name": f"Store {i:02d}",
            "x": round(x, 1),
            "y": round(y, 1),
            "demand": rng.randint(6, 16),  # pallets / week
        })
        i += 1

network = {
    "description": "Fictional Kmart supply-chain network for AlphaEvolve demo",
    "units": {"distance": "km", "demand": "pallets/week"},
    "truck_capacity": 34,          # pallets per truck route
    "cost_per_km": 2.5,            # AUD per km driven
    "fixed_cost_per_route": 300.0, # AUD per truck dispatched
    "dcs": DCS,
    "stores": stores,
}

out = Path(__file__).parent / "network.json"
out.write_text(json.dumps(network, indent=2))
print(f"wrote {out}: {len(DCS)} DCs, {len(stores)} stores, "
      f"total demand {sum(s['demand'] for s in stores)} pallets")
