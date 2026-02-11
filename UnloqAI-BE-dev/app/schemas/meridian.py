from pydantic import BaseModel
from typing import Optional, Union

class Trend(BaseModel):
    value: float
    direction: str # 'up' | 'down' | 'neutral'

class KPIResponse(BaseModel):
    title: str
    value: Union[float, str]
    unit: str
    trend: Optional[Trend]
    status: str # 'on_track' | 'at_risk' | 'off_track'

class SignalResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    severity: str

class RecommendationResponse(BaseModel):
    id: str
    title: str
    rationale: str
    status: str
    impact_estimate: Optional[str] = None # Mocked for pending

class LedgerEntryResponse(BaseModel):
    id: str
    date: str
    event: str
    impact: str
    status: str

class ChartDataPoint(BaseModel):
    name: str
    investment: float
    return_value: float # 'return' is a keyword in python, so we map it

