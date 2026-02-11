import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, index=True, nullable=False)  # e.g., 'harper', 'oakfield'
    
    decisions = relationship("Decision", back_populates="company")

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    flow_type = Column(String, nullable=False)  # e.g., 'contract_triage', 'options_basket'
    status = Column(String, default="pending")  # 'pending', 'approved'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="decisions")
    impact_ledger = relationship("ImpactLedger", back_populates="decision", uselist=False)
    
    # Relationships to domain specific models
    harper_contract = relationship("HarperContract", back_populates="decision", uselist=False)
    oakfield_bundles = relationship("DecisionBundle", back_populates="decision")

class ImpactLedger(Base):
    __tablename__ = "impact_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"), nullable=False, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    flow_type = Column(String)
    route_type = Column(String)
    risk_level = Column(String)  # 'Low', 'Medium', 'High'
    risk_notes = Column(Text)
    
    # Financials (using Numeric for Decimal)
    options_margin_pct = Column(Numeric)
    margin_target_pct = Column(Numeric)
    margin_delta_pct = Column(Numeric)
    
    # Bundle Opps
    bundle_opportunity_detected = Column(Boolean)
    bundle_opportunity_count = Column(Integer)
    bundle_offer_sent = Column(Boolean)
    bundle_offer_channel = Column(String)
    bundle_estimated_additional_revenue = Column(Numeric)
    bundle_estimated_additional_margin = Column(Numeric)
    
    # Performance
    latency_ms = Column(Integer)
    estimated_time_saved_minutes = Column(Numeric)
    execution_channel = Column(String)
    execution_status = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    decision = relationship("Decision", back_populates="impact_ledger")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    token = Column(String, primary_key=True, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())

