# Hospital Co-Scheduling Optimization — Cymbal Children's Hospital

## Problem

A hospital operates multiple resources (e.g., Operating Theatres) and staff members (surgeons, nurses, anaesthetists) to perform surgeries for patients. Each patient has a specific Demand requiring a surgery of a certain duration and a set of required roles/skills. Staff members have specific roles and sets of skills. Demands must be scheduled within a strict Scheduling Horizon. 

## Objective

Maximise patient appointment throughput, whilst minimising resource idle time, overtime hours, and staff fatigue violations.

The objective score is calculated by the local evaluator as follows:
score = (patients_scheduled * weights.throughput)
        - (idle_hours * weights.idle_time_penalty)
        - (overtime_hours * weights.overtime_penalty)
        - (fatigue_violations * 50.0)

A higher score is better. Fatigue violations occur when a staff member has less than `minRestHoursBetweenShifts` of rest between overlapping or sequential appointments. Overtime occurs if an appointment extends outside the `schedulingHorizon`.

## Contract for build_schedule (the evolve block)

```python
build_schedule(config: dict) -> list[dict]
```

- `config`: A dictionary containing `resources`, `staff`, `patients`, `demands`, and `heuristics`.
- Return a list of appointment dictionaries with the following structure:
  `{"id": str, "demandId": str, "resourceId": str, "startTime": str, "endTime": str, "staffIds": list[str]}`

Hard feasibility rules (violations score as failure and reject the candidate):
- `resourceId` must be valid, and no Resource can be double-booked (no overlapping appointments).
- `demandId` must be valid, and scheduled at most once.
- `staffIds` must be valid, no duplicate staff in the same appointment, and no Staff member can be double-booked (no overlapping appointments).
- The Patient linked to the demand must not be scheduled in overlapping appointments (physical impossibility).
- The combined skills of the assigned `staffIds` MUST satisfy EVERY required role for the demand.
- The appointment duration (`endTime - startTime`) MUST exactly match the demand's `durationMinutes`.

## Guidance

- The baseline is a naive First-Come-First-Served greedy packing strategy that picks the earliest available 15-minute slot for both resource and staff.
- Known-better directions: intelligent bin-packing of surgeries to minimise idle time gaps, smart staff assignment to avoid fatigue violations (rest gaps), and choosing appointment order to maximise throughput within the horizon.
- Must be deterministic (no randomness, or fixed seeds only) and pure Python standard library. Keep runtime fast; the instance is small.
- The helpers `str_to_mins(t)`, `mins_to_str(m)`, and `overlaps(s1, e1, s2, e2)` are available outside the evolve block, as is `math`.
