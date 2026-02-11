from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class HarperContractBase(BaseModel):
    decision_id: UUID
    client_name: str
    matter_ref: str
    contract_type: str
    s3_key: str
    received_at: Optional[datetime] = None
    sector: Optional[str] = None
    complexity_band: Optional[str] = None
    risk_band: Optional[str] = None
    review_status: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    partner_approved_at: Optional[datetime] = None
    estimated_time_normal_minutes: Optional[int] = None
    estimated_time_ai_minutes: Optional[int] = None
    fee_model: Optional[str] = None
    price_per_contract: Optional[float] = None
    identified_issues: Optional[Dict[str, Any]] = None
    summary_text: Optional[str] = None

class HarperContractCreate(HarperContractBase):
    pass

class HarperContractUpdate(BaseModel):
    client_name: Optional[str] = None
    review_status: Optional[str] = None
    risk_band: Optional[str] = None
    # Add other fields as needed for updates

class HarperContractResponse(HarperContractBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class HarperBenchmarkBase(BaseModel):
    matter_type: str
    sector: str
    avg_market_fee: float
    avg_market_hours: float

class HarperBenchmarkCreate(HarperBenchmarkBase):
    pass

class HarperBenchmarkResponse(HarperBenchmarkBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
