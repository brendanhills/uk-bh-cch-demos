"""Cymbal Children's Hospital Co-Scheduling - seed program for AlphaEvolve.

Only build_schedule() between the EVOLVE-BLOCK markers may be changed. 
It must return a list of dicts:
[{"id": str, "demandId": str, "resourceId": str, "day": str, "startTime": str, "endTime": str, "staffIds": list[str], "priority": int}, ...]
"""
import math

def str_to_mins(t: str) -> int:
    """Converts a 'HH:MM' time string to absolute minutes since midnight."""
    h, m = map(int, t.split(':'))
    return h * 60 + m


def mins_to_str(m: int) -> str:
    """Converts absolute minutes since midnight to a 'HH:MM' string."""
    return f"{m // 60:02d}:{m % 60:02d}"


def overlaps(s1: int, e1: int, s2: int, e2: int) -> bool:
    """Checks if two time intervals strictly overlap."""
    return s1 < e2 and s2 < e1


def is_staff_qualified(staff_member: dict, role: str) -> bool:
    """Immutable domain rule: Checks if a staff member has the required specialist skill or role."""
    return role in staff_member.get("skills", []) or role == staff_member.get("role")


def is_interval_free(schedule_list: list, current_time: int, end_time: int) -> bool:
    """Immutable domain rule: Checks if a resource or staff schedule is free during [current_time, end_time]."""
    for s_mins, e_mins in schedule_list:
        if overlaps(current_time, end_time, s_mins, e_mins):
            return False
    return True


# EVOLVE-BLOCK-START
def build_schedule(config):
    """Baseline heuristic: Multi-day priority greedy packing with specialist skill matching.
    
    Tries to schedule each demand at the earliest possible day and time slot
    where OT and qualified specialist staff are available, balancing workload.
    """
    resources = config["resources"]
    staff = config["staff"]
    demands = config["demands"]
    heuristics = config["heuristics"]
    unavailability = config.get("unavailability", [])
    
    days = heuristics.get("schedulingHorizon", {}).get("days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    start_horizon = str_to_mins(heuristics["schedulingHorizon"]["startTime"])
    end_horizon = str_to_mins(heuristics["schedulingHorizon"]["endTime"])
    
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Pre-fill unavailability slots
    resource_schedules = {r["id"]: [] for r in resources}
    for u in unavailability:
        r_id = u.get("resourceId")
        u_day = u.get("day", "Tuesday")
        d_idx = DAYS.index(u_day) if u_day in DAYS else 0
        s_mins = d_idx * 1440 + str_to_mins(u.get("startTime", "10:00"))
        e_mins = d_idx * 1440 + str_to_mins(u.get("endTime", "14:00"))
        if r_id in resource_schedules:
            resource_schedules[r_id].append((s_mins, e_mins))
            
    staff_schedules = {s["id"]: [] for s in staff}
    patient_scheduled = set()
    
    schedules = []
    appt_counter = 1
    step_interval = 10
    
    # Priority sorting: Emergency (0) > Urgent (1) > Routine (2)
    sorted_demands = sorted(demands, key=lambda d: d.get("priority", 2))
    
    for demand in sorted_demands:
        duration = demand["durationMinutes"]
        required_roles = demand["requiredRoles"]
        demand_id = demand["id"]
        patient_id = demand["patientId"]
        priority = demand.get("priority", 2)
        
        if patient_id in patient_scheduled:
            continue
            
        scheduled = False
        
        for d_idx, day_name in enumerate(days):
            if scheduled:
                break
                
            day_offset = d_idx * 1440
            day_start = day_offset + start_horizon
            day_end = day_offset + end_horizon
            
            for current_time in range(day_start, day_end - duration + 1, step_interval):
                end_time = current_time + duration
                
                # 1. Find an available Resource (Operating Theatre)
                available_resource = None
                for r in resources:
                    if is_interval_free(resource_schedules[r["id"]], current_time, end_time):
                        available_resource = r
                        break
                        
                if not available_resource:
                    continue
                    
                # 2. Find available Staff using Immutable Skill Matching & Dynamic Workload Balancing
                assigned_staff = []
                role_satisfied = True
                for role in required_roles:
                    assigned_ids = [st["id"] for st in assigned_staff]
                    
                    # Match specialist skills using immutable helper function
                    candidates = [
                        s for s in staff 
                        if is_staff_qualified(s, role) and s["id"] not in assigned_ids
                    ]
                    
                    # Heuristic ranking (AlphaEvolve can mutate how staff candidates are prioritized)
                    candidates.sort(key=lambda s: sum(e - st for st, e in staff_schedules[s["id"]]))
                    
                    found_staff = None
                    for s in candidates:
                        if is_interval_free(staff_schedules[s["id"]], current_time, end_time):
                            found_staff = s
                            break
                            
                    if found_staff:
                        assigned_staff.append(found_staff)
                    else:
                        role_satisfied = False
                        break
                        
                # 3. Schedule Appointment
                if role_satisfied and available_resource:
                    start_str = mins_to_str(current_time - day_offset)
                    end_str = mins_to_str(end_time - day_offset)
                    
                    schedules.append({
                        "id": f"A{appt_counter}",
                        "demandId": demand_id,
                        "resourceId": available_resource["id"],
                        "day": day_name,
                        "startTime": start_str,
                        "endTime": end_str,
                        "staffIds": [s["id"] for s in assigned_staff],
                        "priority": priority
                    })
                    appt_counter += 1
                    
                    resource_schedules[available_resource["id"]].append((current_time, end_time))
                    for s in assigned_staff:
                        staff_schedules[s["id"]].append((current_time, end_time))
                    patient_scheduled.add(patient_id)
                    
                    scheduled = True
                    break
                    
    return schedules
# EVOLVE-BLOCK-END

def solve(config):
    """Entrypoint function called directly by the AlphaEvolve engine."""
    return build_schedule(config)
