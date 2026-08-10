#!/usr/bin/env python3
"""Backfill per-candidate routes into traces/evolution_trace.json for the UI.

The recorded run only stored routes for new-best candidates. So the map can
move on every replay tick, this script reconstructs a *feasible, cost-matched
illustrative* plan for every other feasible candidate: a seeded local search
that starts from the best-so-far real plan and walks its primary-instance cost
to the candidate's real recorded score. Reconstructed plans are marked
`routes_illustrative: true`; real recorded routes are left untouched.

Deterministic (seeded per candidate idx). Writes a one-time backup to
traces/evolution_trace.orig.json.
"""
import copy
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiment"))
from evaluate import load_instances, plan_cost  # noqa: E402

TRACE = ROOT / "traces" / "evolution_trace.json"
BACKUP = ROOT / "traces" / "evolution_trace.orig.json"
TOL = 0.003          # accept within 0.3% of target cost
MAX_ITERS = 6000


def try_cost(inst, routes):
    try:
        return plan_cost(inst, routes)
    except ValueError:
        return None


def reconstruct(inst, start_routes, target, seed):
    """Seeded local search: mutate a feasible plan until its cost ~= target."""
    rng = random.Random(seed)
    cap = inst["truck_capacity"]
    demand = {s["id"]: s["demand"] for s in inst["stores"]}
    dc_ids = [d["id"] for d in inst["dcs"]]

    routes = copy.deepcopy(start_routes)
    cost = plan_cost(inst, routes)
    best_gap = abs(cost - target)

    for _ in range(MAX_ITERS):
        if best_gap / target <= TOL:
            break
        cand = copy.deepcopy(routes)
        move = rng.random()
        if move < 0.45 and len(cand) > 1:
            # relocate a store to another (or new) route
            src = rng.choice(cand)
            if not src["stores"]:
                continue
            sid = src["stores"].pop(rng.randrange(len(src["stores"])))
            if rng.random() < 0.12:
                cand.append({"dc": rng.choice(dc_ids), "stores": [sid]})
            else:
                dst = rng.choice(cand)
                load = sum(demand[x] for x in dst["stores"])
                if dst is src or load + demand[sid] > cap:
                    continue
                dst["stores"].insert(rng.randrange(len(dst["stores"]) + 1), sid)
            cand = [r for r in cand if r["stores"]]
        elif move < 0.75 and len(cand) > 1:
            # swap two stores between routes
            r1, r2 = rng.sample(cand, 2)
            if not r1["stores"] or not r2["stores"]:
                continue
            i, j = rng.randrange(len(r1["stores"])), rng.randrange(len(r2["stores"]))
            r1["stores"][i], r2["stores"][j] = r2["stores"][j], r1["stores"][i]
        else:
            # reverse a segment within one route
            r = rng.choice(cand)
            if len(r["stores"]) < 3:
                continue
            i, j = sorted(rng.sample(range(len(r["stores"])), 2))
            r["stores"][i:j + 1] = reversed(r["stores"][i:j + 1])

        c = try_cost(inst, cand)
        if c is None:
            continue
        gap = abs(c - target)
        if gap < best_gap:
            routes, cost, best_gap = cand, c, gap
    return routes, cost


def main():
    trace = json.loads(TRACE.read_text())
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps(trace, indent=1))
        print(f"backup written: {BACKUP.name}")

    primary = load_instances()[0]

    # primary cost / mean cost ratio, calibrated on points where both are known
    known = [trace["baseline"]] + [c for c in trace["candidates"]
                                   if c.get("routes") and c.get("score") is not None]
    ratio = sum(k["primary_cost"] / -k["score"] for k in known) / len(known)

    best_plan = trace["baseline"]["routes"]
    done = 0
    for c in trace["candidates"]:
        if c.get("score") is None:
            continue  # infeasible: no plan exists
        if c.get("routes"):
            best_plan = c["routes"]  # real recorded plan, keep as-is
            continue
        # calibration can land just below the best-so-far plan's cost, which a
        # non-best candidate can't beat by definition — clamp up to it
        floor = plan_cost(primary, best_plan)
        target = max(-c["score"] * ratio, floor * 1.001)
        routes, cost = reconstruct(primary, best_plan, target, seed=c["idx"])
        plan_cost(primary, routes)  # assert feasibility
        c["routes"] = routes
        c["routes_illustrative"] = True
        done += 1

    TRACE.write_text(json.dumps(trace, indent=1))
    total = sum(1 for c in trace["candidates"] if c.get("score") is not None)
    print(f"reconstructed {done} illustrative plans ({total} feasible candidates)")


if __name__ == "__main__":
    main()
