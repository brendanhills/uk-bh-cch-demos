from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class CamelBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore"  # Allow fields gracefully for forward-compatibility
    )

class SchedulingHorizon(CamelBaseModel):
    start_time: str
    end_time: str
    days: Optional[List[str]] = None

class FatigueManagement(CamelBaseModel):
    min_rest_hours_between_shifts: int

class BudgetControl(CamelBaseModel):
    standard_rate_per_hour: float
    overtime_multiplier: float

class ObjectiveWeights(CamelBaseModel):
    throughput: float
    idle_time_penalty: float
    overtime_penalty: float

class Heuristics(CamelBaseModel):
    scheduling_horizon: SchedulingHorizon
    fatigue_management: FatigueManagement
    budget_control: BudgetControl
    objective_weights: ObjectiveWeights

class Resource(CamelBaseModel):
    id: str
    name: str
    type: str

class Staff(CamelBaseModel):
    id: str
    name: str
    role: str
    skills: List[str]

class Patient(CamelBaseModel):
    id: str
    name: str
    priority: Optional[int] = 2

class Demand(CamelBaseModel):
    id: str
    patient_id: str
    surgery_type: str
    duration_minutes: int
    required_roles: List[str]
    priority: int = 2

class UnavailabilitySlot(CamelBaseModel):
    resource_id: str
    day: str
    start_time: str
    end_time: str
    reason: Optional[str] = "Maintenance"

class Config(CamelBaseModel):
    schema_url: Optional[str] = Field(default=None, alias="$schema")
    heuristics: Heuristics
    unavailability: Optional[List[UnavailabilitySlot]] = None
    resources: List[Resource]
    staff: List[Staff]
    patients: List[Patient]
    demands: List[Demand]

def load_config(file_path: str = "data/config.json") -> Config:
    """Loads and validates the scenario configuration from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return Config.model_validate_json(f.read())


if __name__ == "__main__":
    import sys
    try:
        cfg = load_config()
        print("Successfully loaded and validated configuration.")
        print(
            f"Resources: {len(cfg.resources)}, "
            f"Staff: {len(cfg.staff)}, "
            f"Patients: {len(cfg.patients)}, "
            f"Demands: {len(cfg.demands)}"
        )
    except Exception as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)
