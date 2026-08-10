from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

@dataclass
class TimeSlot:
    start_minutes: int
    end_minutes: int

    def overlaps(self, other: 'TimeSlot') -> bool:
        return self.start_minutes < other.end_minutes and other.start_minutes < self.end_minutes

    @property
    def duration(self) -> int:
        return self.end_minutes - self.start_minutes

    @staticmethod
    def str_to_mins(t: str) -> int:
        h, m = map(int, t.split(':'))
        return h * 60 + m

    @classmethod
    def from_str(cls, start_str: str, end_str: str, day: str = "Monday") -> 'TimeSlot':
        day_index = DAYS.index(day) if day in DAYS else 0
        start = (day_index * 1440) + cls.str_to_mins(start_str)
        end = (day_index * 1440) + cls.str_to_mins(end_str)
        return cls(start, end)

@dataclass
class Resource:
    id: str
    name: str
    type: str

@dataclass
class Staff:
    id: str
    name: str
    role: str
    skills: Set[str]

    def has_skill(self, skill: str) -> bool:
        return skill in self.skills

@dataclass
class Patient:
    id: str
    name: str
    priority: int = 2

@dataclass
class Appointment:
    id: str
    patient: Patient
    resource: Resource
    time_slot: TimeSlot
    staff: List[Staff]
    day: str = "Monday"
    priority: int = 2

class Schedule:
    def __init__(self):
        self.appointments: List[Appointment] = []
        self._resource_schedule: Dict[str, List[TimeSlot]] = {}
        self._staff_schedule: Dict[str, List[TimeSlot]] = {}
        self._patient_schedule: Dict[str, List[TimeSlot]] = {}
        self._unavailability: Dict[str, List[TimeSlot]] = {}

    def add_unavailability(self, resource_id: str, time_slot: TimeSlot):
        if resource_id not in self._unavailability:
            self._unavailability[resource_id] = []
        self._unavailability[resource_id].append(time_slot)

    def add_appointment(self, appt: Appointment):
        self.appointments.append(appt)
        
        if appt.resource.id not in self._resource_schedule:
            self._resource_schedule[appt.resource.id] = []
        self._resource_schedule[appt.resource.id].append(appt.time_slot)
        
        for s in appt.staff:
            if s.id not in self._staff_schedule:
                self._staff_schedule[s.id] = []
            self._staff_schedule[s.id].append(appt.time_slot)
            
        if appt.patient.id not in self._patient_schedule:
            self._patient_schedule[appt.patient.id] = []
        self._patient_schedule[appt.patient.id].append(appt.time_slot)

    def has_resource_overlap(self, resource_id: str, time_slot: TimeSlot) -> bool:
        slots = self._resource_schedule.get(resource_id, [])
        if any(s.overlaps(time_slot) for s in slots):
            return True
        unavail = self._unavailability.get(resource_id, [])
        return any(u.overlaps(time_slot) for u in unavail)

    def has_staff_overlap(self, staff_id: str, time_slot: TimeSlot) -> bool:
        slots = self._staff_schedule.get(staff_id, [])
        return any(s.overlaps(time_slot) for s in slots)

    def has_patient_overlap(self, patient_id: str, time_slot: TimeSlot) -> bool:
        slots = self._patient_schedule.get(patient_id, [])
        return any(s.overlaps(time_slot) for s in slots)

    def get_staff_rest_violations(self, staff_id: str, min_rest_minutes: int) -> int:
        """Returns the number of fatigue violations for a staff member.
        
        Checks:
        1. Overwork violation if total procedure time on any single day > 8 hours (480m).
        2. Overnight rest gap between consecutive days < min_rest_minutes.
        """
        slots = self._staff_schedule.get(staff_id, [])
        if not slots:
            return 0
        
        day_slots: Dict[int, List[TimeSlot]] = {}
        for s in slots:
            day_idx = s.start_minutes // 1440
            if day_idx not in day_slots:
                day_slots[day_idx] = []
            day_slots[day_idx].append(s)
            
        violations = 0
        
        # 1. Overwork per day (> 8 hours)
        for day_idx, d_slots in day_slots.items():
            total_mins = sum(s.duration for s in d_slots)
            if total_mins > 480:
                violations += 1
                
        # 2. Overnight rest gap between consecutive days
        sorted_days = sorted(day_slots.keys())
        for i in range(len(sorted_days) - 1):
            d1 = sorted_days[i]
            d2 = sorted_days[i+1]
            if d2 == d1 + 1:
                last_end = max(s.end_minutes for s in day_slots[d1])
                first_start = min(s.start_minutes for s in day_slots[d2])
                gap = first_start - last_end
                if gap < min_rest_minutes:
                    violations += 1
                    
        return violations
