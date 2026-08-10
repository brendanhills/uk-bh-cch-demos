# Product Definition: RCH Resource & Staff Co-Scheduling x AlphaEvolve

## Vision
A Proof of Concept (PoC) and demonstration of adapting the AlphaEvolve evolutionary optimization framework for the Cymbal Children's Hospital (CCH). The project replaces the baseline supply-chain truck-routing logic with an integrated hospital resource and staff co-scheduling system. AlphaEvolve will be used to rewrite complex scheduling heuristics over multiple candidate programs to optimize for hospital-specific metrics (e.g., co-scheduling staff, rooms, and patients), with results visualized in a **highly engaging, interactive static web UI designed to deliver a 'wow' factor for non-technical stakeholders (building upon the visual impact of the original Kmart demo).**

**Non-Functional Goal:** This is a non-production demonstration aimed at showcasing what is possible with AlphaEvolve, prioritizing **impressive visualization, algorithmic clarity, and fast iteration** over production-grade robustness.

## Scope
To ensure fast iteration and algorithmic clarity for the demo, we will use a phased approach. 

### Phase 1: MVP Pilot
The initial PoC implementation will focus on a tightly bounded co-scheduling subset:
- **High-Value Resources:** Limited to 2 specific resources (e.g., 2 Operating Theatres).
- **Staff Roles:** A small pool of key staff required for these resources (e.g., Surgeons and Nurses).
- **Demand:** Patient Appointments / Surgeries requiring co-scheduling of the 2 resources and staff.
- **Scheduling Horizon:** Weekly Roster with standard 8 and 12-hour shifts.
- **Skill & Role Matching:** Strictly matching Surgeon and Nurse specialist skills to each surgical operation.
- **Executive Storytelling:** A structured 3-Phase workflow (Before -> Evolution -> After) enabling interactive presenter changes (multi-week stepping, unplanned disruption injections) under a default Live AlphaEvolve API execution mode.

### Future Phases
Subsequent iterations can scale to include:
- Additional staff roles (Admin, Allied Health).
- More equipment types, beds, and complex clinic appointments.
- Advanced fairness rules and multi-site management.

## Constraints & Requirements (Phase 1 Focus)
AlphaEvolve will be guided by the following core constraints and evaluator rules:
- **Resource Co-scheduling:** Ensuring that the required Staff, specific Room/Equipment, and Patient are all available and assigned simultaneously.
- **Skill & Role Matching:** Strictly matching Surgeon and Nurse specialist skills (e.g., Pediatric Neuro, Cardiac, Orthopedic) to the specific surgical operation.
- **Fatigue Management:** Enforcing minimum rest hours between shifts.
- **Budget Control:** Minimizing reliance on overtime.

## Optimization Goal
The primary objective function for the evolutionary algorithm is to:
**Maximize Patient Appointment/Surgery Throughput while minimizing resource idle time and staff overtime.**
