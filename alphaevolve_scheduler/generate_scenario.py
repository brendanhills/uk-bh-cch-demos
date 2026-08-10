import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NUM_ROOMS = 5
NUM_PATIENTS = 160

HEURISTICS = {
    "schedulingHorizon": {
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "startTime": "08:00",
        "endTime": "20:00"
    },
    "fatigueManagement": {
        "minRestHoursBetweenShifts": 10
    },
    "budgetControl": {
        "standardRatePerHour": 100,
        "overtimeMultiplier": 1.5
    },
    "objectiveWeights": {
        "throughput": 100,
        "idleTimePenalty": 1,
        "overtimePenalty": 2
    }
}

UNAVAILABILITY = [
    {
        "resourceId": "OT_2",
        "day": "Tuesday",
        "startTime": "10:00",
        "endTime": "14:00",
        "reason": "Unscheduled Maintenance"
    }
]


def generate():
    """Generates a 150-patient scenario with 7 Surgeons and 9 Nurses."""
    random.seed(42)
    
    resources = []
    for i in range(1, NUM_ROOMS + 1):
        resources.append({
            "id": f"OT_{i}",
            "name": f"Operating Theatre {i}",
            "type": "Operating Theatre"
        })
        
    surgeon_data = [
        ("S1", "Dr. A. Chen", ["Surgeon", "Pediatric Neuro"]),
        ("S2", "Dr. B. Patel", ["Surgeon", "Pediatric Neuro"]),
        ("S3", "Dr. C. Smith", ["Surgeon", "Cardiac"]),
        ("S4", "Dr. D. Williams", ["Surgeon", "Cardiac"]),
        ("S5", "Dr. E. Taylor", ["Surgeon", "Orthopedic"]),
        ("S6", "Dr. F. Anderson", ["Surgeon", "General"]),
        ("S7", "Dr. G. Roberts", ["Surgeon", "Pediatric Neuro"])
    ]
    
    nurse_data = [
        ("N1", "Nurse H. Miller", ["Nurse", "Pediatric Neuro"]),
        ("N2", "Nurse I. Davis", ["Nurse", "Cardiac"]),
        ("N3", "Nurse J. Wilson", ["Nurse", "Orthopedic"]),
        ("N4", "Nurse K. Martinez", ["Nurse", "General"]),
        ("N5", "Nurse L. Taylor", ["Nurse", "General"]),
        ("N6", "Nurse M. White", ["Nurse", "General"]),
        ("N7", "Nurse N. Harris", ["Nurse", "General"]),
        ("N8", "Nurse O. Clark", ["Nurse", "General"]),
        ("N9", "Nurse P. Thomas", ["Nurse", "General"])
    ]

    staff = []
    for s_id, name, skills in surgeon_data:
        staff.append({
            "id": s_id,
            "name": name,
            "role": "Surgeon",
            "skills": skills
        })
    for n_id, name, skills in nurse_data:
        staff.append({
            "id": n_id,
            "name": name,
            "role": "Nurse",
            "skills": skills
        })
        
    patients = []
    demands = []
    
    surgery_types = [
        ("Pediatric Brain Tumor Resection", 180, ["Pediatric Neuro", "Nurse"]),
        ("Open Heart Valve Repair", 210, ["Cardiac", "Cardiac"]),
        ("Complex Spinal Reconstruction", 150, ["Orthopedic", "Nurse"]),
        ("Emergency Trauma Surgery", 120, ["Surgeon", "Nurse"]),
        ("Knee Arthroscopy", 90, ["Orthopedic", "Nurse"]),
        ("Appendectomy", 90, ["General", "Nurse"]),
        ("Gallbladder Removal", 120, ["General", "Nurse"])
    ]
    
    for i in range(1, NUM_PATIENTS + 1):
        p_id = f"P{i}"
        
        rand_val = random.random()
        if rand_val < 0.05:
            priority = 0
        elif rand_val < 0.30:
            priority = 1
        else:
            priority = 2
            
        patients.append({
            "id": p_id,
            "name": f"Patient {i}",
            "priority": priority
        })
        
        s_type, base_duration, req_roles = random.choice(surgery_types)
        duration = base_duration + random.choice([-15, 0, 15])
        
        demands.append({
            "id": f"D{i}",
            "patientId": p_id,
            "surgeryType": s_type,
            "durationMinutes": max(45, duration),
            "requiredRoles": req_roles,
            "priority": priority
        })
        
    config = {
        "$schema": "./config.schema.json",
        "heuristics": HEURISTICS,
        "unavailability": UNAVAILABILITY,
        "resources": resources,
        "staff": staff,
        "patients": patients,
        "demands": demands
    }
    
    out_path = ROOT / "data" / "config.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with out_path.open("w") as f:
        json.dump(config, f, indent=2)
        
    print(f"✨ Successfully generated enterprise scenario:")
    print(f"   - {NUM_ROOMS} Rooms")
    print(f"   - 7 Specialized Surgeons & 9 Specialized Nurses")
    print(f"   - {NUM_PATIENTS} Patients across 5-day horizon (Mon-Fri)")
    print(f"   - Overwritten {out_path}")

if __name__ == "__main__":
    generate()
