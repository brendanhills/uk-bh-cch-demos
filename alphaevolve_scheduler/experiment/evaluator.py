import sys
import signal
import copy
import ast
import traceback
from typing import List, Dict, Any
from models import Schedule, Appointment, Resource, Staff, Patient, TimeSlot
from config import Config, load_config

FAIL_SCORE = -1000.0

FORBIDDEN_IMPORTS = {"sys", "os", "subprocess", "shutil", "builtins", "inspect"}
FORBIDDEN_NAMES = {"_getframe", "eval", "exec", "compile", "__import__", "globals", "locals"}

class InfeasibilityError(ValueError):
    pass

def validate_ast_security(candidate_code: str) -> None:
    """Pre-evaluates candidate code AST to prevent stack manipulation, file ops, or reward hacking."""
    try:
        tree = ast.parse(candidate_code)
    except SyntaxError as se:
        raise InfeasibilityError(f"Syntax error in candidate code: {se}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in FORBIDDEN_IMPORTS:
                    raise InfeasibilityError(f"Forbidden import '{alias.name}' detected")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in FORBIDDEN_IMPORTS:
                raise InfeasibilityError(f"Forbidden import module '{node.module}' detected")
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES:
                raise InfeasibilityError(f"Forbidden function or attribute '{node.id}' detected")

def create_multi_benchmark_configs(base_config: Config) -> List[Dict[str, Any]]:
    """Creates 3 distinct benchmark scenario configs to prevent algorithm overfitting:
    - Scenario A (Standard): Full 5-day horizon baseline
    - Scenario B (Staff Shortage): Nurse N1 and Surgeon S1 absent
    - Scenario C (OT_1 Maintenance): OT_1 unavailable all Thursday
    """
    raw_base = {
        "resources": [r.model_dump(by_alias=True) for r in base_config.resources],
        "staff": [s.model_dump(by_alias=True) for s in base_config.staff],
        "patients": [p.model_dump(by_alias=True) for p in base_config.patients],
        "demands": [d.model_dump(by_alias=True) for d in base_config.demands],
        "heuristics": base_config.heuristics.model_dump(by_alias=True),
        "unavailability": [u.model_dump(by_alias=True) for u in base_config.unavailability] if base_config.unavailability else []
    }
    
    # Scenario A: Base Standard
    scen_a = raw_base
    
    # Scenario B: Staff Shortage (Nurse N1 and Surgeon S1 on leave)
    scen_b = copy.deepcopy(raw_base)
    scen_b["staff"] = [s for s in scen_b["staff"] if s["id"] not in ("N1", "S1")]
    
    # Scenario C: Full Day Maintenance on OT_1
    scen_c = copy.deepcopy(raw_base)
    scen_c["unavailability"].append({"resourceId": "OT_1", "day": "Thursday", "startTime": "08:00", "endTime": "18:00"})
    
    return [
        {"name": "Standard Horizon", "weight": 0.5, "raw": scen_a, "typed": base_config},
        {"name": "Staff Shortage", "weight": 0.25, "raw": scen_b, "typed": Config(**scen_b)},
        {"name": "OT_1 Thursday Maintenance", "weight": 0.25, "raw": scen_c, "typed": Config(**scen_c)}
    ]

def evaluate_schedule(
    candidate_schedule: List[Dict[str, Any]], config: Config
) -> Dict[str, float]:
    """Evaluates a schedule against strict hard and soft constraints."""
    resources = {r.id: Resource(**r.model_dump()) for r in config.resources}
    staff = {
        s.id: Staff(
            id=s.id, name=s.name, role=s.role, skills=set(s.skills)
        ) for s in config.staff
    }
    patients = {p.id: Patient(**p.model_dump()) for p in config.patients}
    demands = {d.id: d for d in config.demands}
    
    schedule = Schedule()
    seen_demands = set()
    seen_patients = set()
    overtime_minutes = 0
    
    # Inject resource unavailability (maintenance slots) if defined in config
    unavail_list = getattr(config, "unavailability", []) or []
    if isinstance(unavail_list, list):
        for u in unavail_list:
            if isinstance(u, dict):
                r_id = u.get("resourceId")
                day = u.get("day", "Tuesday")
                st = u.get("startTime", "10:00")
                et = u.get("endTime", "14:00")
            else:
                r_id = getattr(u, "resource_id", None)
                day = getattr(u, "day", "Tuesday")
                st = getattr(u, "start_time", "10:00")
                et = getattr(u, "end_time", "14:00")
            if r_id and r_id in resources:
                u_slot = TimeSlot.from_str(st, et, day=day)
                schedule.add_unavailability(r_id, u_slot)

    horizon_start = TimeSlot.str_to_mins(config.heuristics.scheduling_horizon.start_time)
    horizon_end = TimeSlot.str_to_mins(config.heuristics.scheduling_horizon.end_time)
    
    for appt_dict in candidate_schedule:
        appt_id = appt_dict.get("id")
        demand_id = appt_dict.get("demandId")
        if not demand_id and appt_dict.get("patientId"):
            pid = str(appt_dict.get("patientId"))
            if pid.startswith("P"):
                demand_id = "D" + pid[1:]
        resource_id = appt_dict.get("resourceId")
        start_time = appt_dict.get("startTime")
        end_time = appt_dict.get("endTime")
        day = appt_dict.get("day", "Monday")
        staff_ids = appt_dict.get("staffIds", [])
        
        if not appt_id:
            raise InfeasibilityError("Missing appointment id")
        if not demand_id or demand_id not in demands:
            raise InfeasibilityError(f"Invalid or missing demandId: {demand_id}")
        if not resource_id or resource_id not in resources:
            raise InfeasibilityError(f"Invalid or missing resourceId: {resource_id}")
        
        if demand_id in seen_demands:
            raise InfeasibilityError(f"Demand {demand_id} scheduled multiple times")
        seen_demands.add(demand_id)
        
        demand = demands[demand_id]
        patient_id = demand.patient_id
        
        if patient_id in seen_patients:
            raise InfeasibilityError(f"Patient {patient_id} scheduled multiple times")
        seen_patients.add(patient_id)
        
        time_slot = TimeSlot.from_str(start_time, end_time, day=day)
        if time_slot.duration != demand.duration_minutes:
            raise InfeasibilityError(
                f"Appointment duration {time_slot.duration}m "
                f"does not match demand {demand.duration_minutes}m"
            )
            
        # Hard Constraints: Overlaps & Unavailability
        if schedule.has_resource_overlap(resource_id, time_slot):
            raise InfeasibilityError(f"Resource {resource_id} is double-booked or in maintenance")
            
        if len(set(staff_ids)) != len(staff_ids):
            raise InfeasibilityError(f"Duplicate staff assigned to appointment {appt_id}")
            
        for s_id in staff_ids:
            if s_id not in staff:
                raise InfeasibilityError(f"Invalid staffId: {s_id}")
            if schedule.has_staff_overlap(s_id, time_slot):
                raise InfeasibilityError(f"Staff {s_id} is double-booked")
                
        # Hard Constraint: Skill/Role Matching
        assigned_staff = [staff[s_id] for s_id in staff_ids]
        for role in demand.required_roles:
            if not any(s.has_skill(role) for s in assigned_staff):
                raise InfeasibilityError(f"Missing required role {role} for demand {demand_id}")
                
        priority = appt_dict.get("priority", getattr(demand, "priority", 2))
        appt = Appointment(appt_id, patients[patient_id], resources[resource_id], time_slot, assigned_staff, day=day, priority=priority)
        schedule.add_appointment(appt)
        
        # Calculate Overtime (relative to daily horizon)
        slot_start_daily = TimeSlot.str_to_mins(start_time)
        slot_end_daily = TimeSlot.str_to_mins(end_time)
        if slot_end_daily > horizon_end:
            overtime_minutes += (slot_end_daily - horizon_end)
        if slot_start_daily < horizon_start:
            overtime_minutes += (horizon_start - slot_start_daily)
            
    total_fatigue_violations = 0
    min_rest_mins = config.heuristics.fatigue_management.min_rest_hours_between_shifts * 60
    for s_id in staff:
        total_fatigue_violations += schedule.get_staff_rest_violations(s_id, min_rest_mins)
        
    patients_scheduled = len(seen_patients)
    overtime_hours = overtime_minutes / 60.0
    days_count = 5
    total_horizon_minutes = (horizon_end - horizon_start) * len(resources) * days_count
    idle_minutes = max(0, total_horizon_minutes - sum(a.time_slot.duration for a in schedule.appointments))
    idle_hours = idle_minutes / 60.0
    
    # 1. Patient Throughput Efficiency Ratio (0.0 to 1.0)
    total_demands_count = len(demands) if len(demands) > 0 else 130
    patient_efficiency = sum(
        1.0 if a.priority == 0 else (0.8 if a.priority == 1 else 0.6)
        for a in schedule.appointments
    ) / total_demands_count
    
    # 2. Resource Idle Efficiency Ratio (0.0 to 1.0)
    idle_efficiency = max(0.0, 1.0 - (idle_minutes / total_horizon_minutes)) if total_horizon_minutes > 0 else 0.0
    
    # 3. Staff Fatigue Rest Break Efficiency (1.0 = zero breaches)
    fatigue_efficiency = max(0.0, 1.0 - (total_fatigue_violations * 0.05))
    
    # 4. Overtime Penalty Ratio
    overtime_penalty_ratio = min(1.0, (overtime_hours * 0.10))
    
    # Rescaled Normalized Multi-Objective Score (0.0 to 100.0 Scale)
    score = round(100.0 * (
        (0.50 * patient_efficiency) +
        (0.25 * idle_efficiency) +
        (0.25 * fatigue_efficiency) -
        (0.10 * overtime_penalty_ratio)
    ), 2)
    
    # Diagnostic insights passed to LLM mutator for targeted bottleneck resolution
    insights = [
        {"label": "patients_scheduled", "text": f"{patients_scheduled}/{len(demands)} surgeries scheduled"},
        {"label": "fatigue_violations", "text": f"{total_fatigue_violations} staff rest violations (<11h rest)"},
        {"label": "idle_time", "text": f"{idle_hours:.1f}h OT gap time"},
        {"label": "overtime", "text": f"{overtime_hours:.1f}h overtime past horizon"}
    ]
    
    return {
        "score": score,
        "patientsScheduled": patients_scheduled,
        "overtimeHours": overtime_hours,
        "resourceIdleTime": idle_minutes,
        "fatigueViolations": total_fatigue_violations,
        "insights": insights
    }

TIMEOUT_SECS = 15

class _Timeout(Exception):
    pass

def _alarm(signum, frame):
    raise _Timeout()

def safe_evaluate(candidate_code: str, config: Config) -> Dict[str, Any]:
    """Executes candidate code across 3 multi-benchmark scenarios to evaluate multi-objective fitness and generalization."""
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(TIMEOUT_SECS)
    ns = {}
    try:
        validate_ast_security(candidate_code)
        exec(candidate_code, ns)
        if "solve" not in ns:
            return {"score": FAIL_SCORE, "error": "Missing 'solve' function", "insights": [{"label": "error", "text": "Missing 'solve' function"}]}
            
        benchmarks = create_multi_benchmark_configs(config)
        total_weighted_score = 0.0
        primary_metrics = None
        primary_schedules = None
        all_insights = []
        
        for b in benchmarks:
            b_name = b["name"]
            b_weight = b["weight"]
            b_raw = b["raw"]
            b_typed = b["typed"]
            
            schedules = ns["solve"](b_raw)
            metrics = evaluate_schedule(schedules, b_typed)
            total_weighted_score += metrics["score"] * b_weight
            
            if b_name == "Standard Horizon":
                primary_metrics = metrics
                primary_schedules = schedules
                
            all_insights.append({
                "label": f"benchmark_{b_name.lower().replace(' ', '_')}",
                "text": f"{b_name}: {metrics['patientsScheduled']} patients, {metrics['fatigueViolations']} fatigue violations, Score: {metrics['score']:.1f}"
            })
            
        primary_metrics["score"] = total_weighted_score
        return {
            "score": total_weighted_score,
            "metrics": primary_metrics,
            "insights": all_insights,
            "schedules": primary_schedules
        }
    except _Timeout:
        return {
            "score": FAIL_SCORE,
            "error": "Evaluation timed out (infinite loop or too slow)",
            "insights": [{"label": "error", "text": "Evaluation timed out"}]
        }
    except InfeasibilityError as ie:
        # Soft gradient penalty for partial infeasibility
        return {
            "score": FAIL_SCORE / 2.0,
            "error": str(ie),
            "insights": [{"label": "constraint_violation", "text": str(ie)}]
        }
    except Exception as e:
        return {
            "score": FAIL_SCORE,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "insights": [{"label": "execution_error", "text": str(e)}]
        }
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
