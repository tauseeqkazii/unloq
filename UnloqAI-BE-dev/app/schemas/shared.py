from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime
from decimal import Decimal


# -------------------------
# Company
# -------------------------

class CompanyBase(BaseModel):
    code: str


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    code: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class CompanyResponse(CompanyBase):
    id: UUID

    model_config = {
        "from_attributes": True
    }

    




# -------------------------
# Decision
# -------------------------

class DecisionBase(BaseModel):
    company_id: UUID
    flow_type: str
    status: Optional[str] = "pending"


class DecisionCreate(DecisionBase):
    pass


class DecisionUpdate(BaseModel):
    flow_type: Optional[str] = None
    status: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class DecisionResponse(DecisionBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Impact Ledger
# -------------------------

class ImpactLedgerBase(BaseModel):
    decision_id: UUID
    company_id: UUID

    flow_type: Optional[str] = None
    route_type: Optional[str] = None
    risk_level: Optional[str] = None
    risk_notes: Optional[str] = None

    options_margin_pct: Optional[Decimal] = None
    margin_target_pct: Optional[Decimal] = None
    margin_delta_pct: Optional[Decimal] = None

    bundle_opportunity_detected: Optional[bool] = None
    bundle_opportunity_count: Optional[int] = None
    bundle_offer_sent: Optional[bool] = None
    bundle_offer_channel: Optional[str] = None
    bundle_estimated_additional_revenue: Optional[Decimal] = None
    bundle_estimated_additional_margin: Optional[Decimal] = None

    latency_ms: Optional[int] = None
    estimated_time_saved_minutes: Optional[Decimal] = None
    execution_channel: Optional[str] = None
    execution_status: Optional[str] = None


class ImpactLedgerCreate(ImpactLedgerBase):
    pass


class ImpactLedgerRead(ImpactLedgerBase):
    id: UUID
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


# -------------------------
# User
# -------------------------

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Token Blacklist
# -------------------------

class TokenBlacklistRead(BaseModel):
    token: str
    blacklisted_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
