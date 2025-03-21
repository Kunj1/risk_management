"""
Data models for the Project Risk Management System.
These models define the structure of data stored in the Supabase database.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskProbability(str, Enum):
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    VERY_LIKELY = "very_likely"


class RiskStatus(str, Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"


class RiskCategory(str, Enum):
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    SCHEDULE = "schedule"
    RESOURCE = "resource"
    MARKET = "market"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    LEGAL = "legal"


@dataclass
class MitigationStrategy:
    """Represents a risk mitigation strategy."""
    description: str
    estimated_cost: float = 0.0
    estimated_effort: int = 0  # in person-days
    effectiveness_rating: int = 0  # scale of 1-10
    assigned_to: Optional[str] = None
    status: str = "proposed"  # proposed, in_progress, completed


@dataclass
class Risk:
    """Represents a project risk."""
    id: Optional[str] = None
    project_id: str = ""
    title: str = ""
    description: str = ""
    category: RiskCategory = RiskCategory.OPERATIONAL
    severity: RiskSeverity = RiskSeverity.MEDIUM
    probability: RiskProbability = RiskProbability.POSSIBLE
    impact_description: str = ""
    status: RiskStatus = RiskStatus.IDENTIFIED
    identified_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    identified_by: Optional[str] = None
    mitigation_strategies: List[MitigationStrategy] = field(default_factory=list)
    risk_score: float = 0.0  # Calculated field
    historical_scores: List[Dict[str, Union[datetime, float]]] = field(default_factory=list)

    def calculate_risk_score(self) -> float:
        """Calculate the risk score based on severity and probability."""
        severity_scores = {
            RiskSeverity.LOW: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.HIGH: 3,
            RiskSeverity.CRITICAL: 4
        }
        
        probability_scores = {
            RiskProbability.UNLIKELY: 1,
            RiskProbability.POSSIBLE: 2,
            RiskProbability.LIKELY: 3,
            RiskProbability.VERY_LIKELY: 4
        }
        
        self.risk_score = severity_scores[self.severity] * probability_scores[self.probability]
        return self.risk_score

    def update_historical_score(self) -> None:
        """Add the current risk score to the historical records."""
        self.historical_scores.append({
            "date": datetime.now(),
            "score": self.risk_score
        })


@dataclass
class Project:
    """Represents a project."""
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    start_date: datetime = field(default_factory=datetime.now)
    expected_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    budget: float = 0.0
    expenditure_to_date: float = 0.0
    status: str = "planning"  # planning, in_progress, on_hold, completed, cancelled
    project_manager: str = ""
    team_members: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)  # List of risk IDs
    health_score: float = 0.0  # Overall health score, calculated field
    current_phase: str = ""
    historical_health_scores: List[Dict[str, Union[datetime, float]]] = field(default_factory=list)

    def calculate_health_score(self, risks: List[Risk]) -> float:
        """Calculate the overall project health score based on risks."""
        if not risks:
            self.health_score = 10.0  # Perfect score if no risks
            return self.health_score
        
        # Calculate average risk score weighted by severity
        total_weighted_score = 0
        total_weight = 0
        
        severity_weights = {
            RiskSeverity.LOW: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.HIGH: 3,
            RiskSeverity.CRITICAL: 4
        }
        
        for risk in risks:
            weight = severity_weights[risk.severity]
            total_weighted_score += risk.risk_score * weight
            total_weight += weight
        
        avg_risk_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Convert to a health score (10 - risk_score)
        # Normalize to ensure it's between 0 and 10
        self.health_score = max(0, min(10, 10 - (avg_risk_score / 1.6)))
        return self.health_score

    def update_historical_health(self) -> None:
        """Add the current health score to historical records."""
        self.historical_health_scores.append({
            "date": datetime.now(),
            "score": self.health_score
        })


@dataclass
class MarketIndicator:
    """Represents an external market indicator."""
    id: Optional[str] = None
    name: str = ""
    category: str = ""  # e.g., economic, technology, regulatory
    current_value: float = 0.0
    previous_value: float = 0.0
    change_percentage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    historical_values: List[Dict[str, Union[datetime, float]]] = field(default_factory=list)
    impact_projects: List[str] = field(default_factory=list)  # List of project IDs
    risk_correlation: Dict[str, float] = field(default_factory=dict)  # Maps risk category to correlation strength


@dataclass
class Alert:
    """Represents a risk alert."""
    id: Optional[str] = None
    project_id: str = ""
    risk_id: Optional[str] = None
    title: str = ""
    description: str = ""
    severity: RiskSeverity = RiskSeverity.MEDIUM
    created_date: datetime = field(default_factory=datetime.now)
    is_read: bool = False
    action_required: bool = False
    action_description: str = ""
    assigned_to: Optional[str] = None