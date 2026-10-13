"""Data models representing TQM Quality tools (Defects, FMEA, PDCA)."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import sqlite3


@dataclass
class Defect:
    """Represents a logged defect or checksheet entry."""
    defect_code: str
    category: str
    description: str
    severity: str
    occurrence_count: int
    status: str
    created_at: str
    corrective_action: Optional[str] = None
    resolved_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Defect":
        return cls(
            id=row["id"],
            defect_code=row["defect_code"],
            category=row["category"],
            description=row["description"],
            severity=row["severity"],
            occurrence_count=int(row["occurrence_count"]),
            status=row["status"],
            corrective_action=row["corrective_action"],
            created_at=row["created_at"],
            resolved_at=row["resolved_at"],
        )


@dataclass
class FMEAItem:
    """Represents a line item in the Failure Mode and Effects Analysis (FMEA)."""
    process_step: str
    failure_mode: str
    failure_effect: str
    potential_cause: str
    existing_controls: str
    severity: int
    occurrence: int
    detection: int
    recommended_action: str
    owner: str
    status: str
    created_at: str
    rpn: Optional[int] = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.rpn is None:
            self.rpn = self.severity * self.occurrence * self.detection

    @property
    def risk_level(self) -> str:
        """Categorizes RPN into high, medium, low based on project threshold."""
        if self.rpn >= 200:
            return "High Risk"
        if self.rpn >= 100:
            return "Medium Risk"
        return "Low Risk"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["risk_level"] = self.risk_level
        return d

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "FMEAItem":
        return cls(
            id=row["id"],
            process_step=row["process_step"],
            failure_mode=row["failure_mode"],
            failure_effect=row["failure_effect"],
            potential_cause=row["potential_cause"],
            existing_controls=row["existing_controls"],
            severity=int(row["severity"]),
            occurrence=int(row["occurrence"]),
            detection=int(row["detection"]),
            rpn=int(row["rpn"]),
            recommended_action=row["recommended_action"],
            owner=row["owner"],
            status=row["status"],
            created_at=row["created_at"],
        )


@dataclass
class PDCARecord:
    """Represents a Plan-Do-Check-Act quality cycle."""
    title: str
    stage: str
    problem_statement: str
    plan_description: str
    owner: str
    status: str
    created_at: str
    updated_at: str
    do_action: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    check_verification: Optional[str] = None
    act_standardization: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "PDCARecord":
        return cls(
            id=row["id"],
            title=row["title"],
            stage=row["stage"],
            problem_statement=row["problem_statement"],
            plan_description=row["plan_description"],
            do_action=row["do_action"],
            expected_result=row["expected_result"],
            actual_result=row["actual_result"],
            check_verification=row["check_verification"],
            act_standardization=row["act_standardization"],
            owner=row["owner"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
