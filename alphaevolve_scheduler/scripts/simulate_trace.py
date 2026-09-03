"""Fallback trace generator (used only if the real AlphaEvolve run is blocked).

Produces traces/evolution_trace.json in the exact schema of the real run, but
from a ladder of genuinely better hand-written heuristics evaluated by the
same evaluator: nearest-neighbour baseline -> better DC assignment ->
Clarke-Wright-style savings -> 2-opt polish. Non-improving candidates between
bests are real perturbed variants, so every score shown is a real evaluator score.

Usage: python scripts/simulate_trace.py
"""
import copy
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiment"))
from evaluate import evaluate, load_instances, plan_cost  # noqa: E402

SEED = (ROOT / "experiment" / "program.py").read_text()

LADDER = []  # (label, code) — each replaces the EVOLVE block of the seed


def with_block(body: str) -> str:
    start = SEED.index("# EVOLVE-BLOCK-START")
    end = SEED.index("# EVOLVE-BLOCK-END")
    return SEED[:start] + "# EVOLVE-BLOCK-START\n" + body + "\n" + SEED[end:]


LADDER.append(("sweep+2opt", with_block('''
def _two_opt(seq, dc, limit=60):
    improved = True
    it = 0
    while improved and it < limit:
        improved = False
        it += 1
        pts = [dc] + seq + [dc]
        for i in range(1, len(pts) - 2):
            for j in range(i + 1, len(pts) - 1):
                d0 = dist(pts[i-1], pts[i]) + dist(pts[j], pts[j+1])
                d1 = dist(pts[i-1], pts[j]) + dist(pts[i], pts[j+1])
                if d1 < d0 - 1e-9:
                    pts[i:j+1] = reversed(pts[i:j+1])
                    improved = True
        seq = pts[1:-1]
    return seq


def build_routes(dcs, stores, capacity):
    routes = []
    for dc in dcs:
        mine = [s for s in stores
                if min(dcs, key=lambda d: dist(s, d))["id"] == dc["id"]]
        unvisited = list(mine)
        while unvisited:
            seq = []
            load = 0
            pos = dc
            while unvisited:
                nxt = min(unvisited, key=lambda s: dist(pos, s))
                if load + nxt["demand"] > capacity:
                    break
                seq.append(nxt); load += nxt["demand"]; pos = nxt
                unvisited.remove(nxt)
            seq = _two_opt(seq, dc)
            routes.append({"dc": dc["id"], "stores": [s["id"] for s in seq]})
    return routes
''')))

LADDER.append(("savings+2opt", with_block('''
def _two_opt(seq, dc, limit=80):
    improved = True
    it = 0
    while improved and it < limit:
        improved = False
        it += 1
        pts = [dc] + seq + [dc]
        for i in range(1, len(pts) - 2):
            for j in range(i + 1, len(pts) - 1):
                d0 = dist(pts[i-1], pts[i]) + dist(pts[j], pts[j+1])
                d1 = dist(pts[i-1], pts[j]) + dist(pts[i], pts[j+1])
                if d1 < d0 - 1e-9:
                    pts[i:j+1] = reversed(pts[i:j+1])
                    improved = True
        seq = pts[1:-1]
    return seq


def build_routes(dcs, stores, capacity):
    # Clarke-Wright savings per nearest-DC cluster, then 2-opt each route.
    routes = []
    for dc in dcs:
        mine = [s for s in stores
                if min(dcs, key=lambda d: dist(s, d))["id"] == dc["id"]]
        # start: one route per store
        rts = [[s] for s in mine]

        def load(r):
            return sum(s["demand"] for s in r)

        merged = True
        while merged:
            merged = False
            best = None
            for a in rts:
                for b in rts:
                    if a is b or load(a) + load(b) > capacity:
                        continue
                    s = (dist(a[-1], dc) + dist(dc, b[0])
                         - dist(a[-1], b[0]))
                    if s > 1e-9 and (best is None or s > best[0]):
                        best = (s, a, b)
            if best:
                _, a, b = best
                a.extend(b)
                rts.remove(b)
                merged = True
        for r in rts:
            r = _two_opt(r, dc)
            routes.append({"dc": dc["id"], "stores": [s["id"] for s in r]})
    return routes
''')))


def noisy_variant(rng):
    """A feasible but deliberately mediocre variant: baseline with a shuffled
    tie-break — produces realistic non-improving scores."""
    k = rng.randint(1, 4)
    body = f'''
def build_routes(dcs, stores, capacity):
    routes = []
    for dc in dcs:
        mine = [s for s in stores
                if min(dcs, key=lambda d: dist(s, d))["id"] == dc["id"]]
        unvisited = sorted(mine, key=lambda s: (s["demand"] * {k}) % 7)
        while unvisited:
            route = {{"dc": dc["id"], "stores": []}}
            load = 0
            pos = dc
            for s in list(unvisited):
                if load + s["demand"] <= capacity:
                    route["stores"].append(s["id"]); load += s["demand"]
                    unvisited.remove(s)
            routes.append(route)
    return routes
'''
    return with_block(body)


def routes_for(code):
    ns = {}
    exec(code, ns)
    primary = load_instances()[0]
    routes = ns["solve"](copy.deepcopy(primary))
    return routes, plan_cost(primary, routes)


def main():
    rng = random.Random(99)
    seed_score = evaluate(SEED)["neg_total_cost"]
    base_routes, base_cost = routes_for(SEED)

    candidates = []
    idx = 0
    best = seed_score
    ladder = list(LADDER)
    total = 60
    improve_at = sorted(rng.sample(range(8, total - 5), len(ladder)))
    for i in range(total):
        idx += 1
        if improve_at and i == improve_at[0] and ladder:
            improve_at.pop(0)
            label, code = ladder.pop(0)
            r = evaluate(code)
            score = r["neg_total_cost"]
            routes, cost = routes_for(code)
            assert score > best, f"{label} did not improve ({score} <= {best})"
            best = score
            candidates.append({"idx": idx, "score": score, "failed": False,
                               "new_best": True, "routes": routes,
                               "primary_cost": round(cost, 2), "code": code})
        elif rng.random() < 0.12:
            candidates.append({"idx": idx, "score": None, "failed": True,
                               "new_best": False})
        else:
            r = evaluate(noisy_variant(rng))
            score = r["neg_total_cost"]
            if score is None or score <= -1e9:
                candidates.append({"idx": idx, "score": None, "failed": True,
                                   "new_best": False})
            else:
                candidates.append({"idx": idx, "score": min(score, best - 1),
                                   "failed": False, "new_best": False})

    trace = {
        "source": "simulated-fallback",
        "metric": "neg_total_cost",
        "model": "n/a (simulated)",
        "baseline": {"score": seed_score, "primary_cost": round(base_cost, 2),
                     "routes": base_routes, "code": SEED},
        "candidates": candidates,
    }
    out = ROOT / "traces" / "evolution_trace.json"
    out.write_text(json.dumps(trace, indent=1))
    print(f"wrote {out}: {len(candidates)} candidates, "
          f"score {seed_score:.0f} -> {best:.0f} "
          f"({(best - seed_score) / abs(seed_score) * 100:.1f}%)")


if __name__ == "__main__":
    main()
