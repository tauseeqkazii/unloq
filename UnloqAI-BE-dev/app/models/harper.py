import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class HarperContract(Base):
    __tablename__ = "harper_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID(as_uuid=True), ForeignKey("decisions.id"), nullable=False, unique=True)
    
    client_name = Column(String, index=True)
    matter_ref = Column(String, index=True)
    contract_type = Column(String)  # 'NDA', 'MSA', etc.
    s3_key = Column(String)
    received_at = Column(DateTime(timezone=True))
    
    sector = Column(String)
    complexity_band = Column(String) # 'low', 'medium', 'high'
    risk_band = Column(String)
    review_status = Column(String)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    partner_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    estimated_time_normal_minutes = Column(Integer)
    estimated_time_ai_minutes = Column(Integer)
    
    fee_model = Column(String) # 'fixed_fee', 'hourly', 'retainer'
    price_per_contract = Column(Float, nullable=True)
    
    identified_issues = Column(JSON)
    summary_text = Column(Text, nullable=True)

    decision = relationship("Decision", back_populates="harper_contract") # From shared

class HarperBenchmark(Base):
    __tablename__ = "harper_benchmarks"

    id = Column(Integer, primary_key=True, index=True) # Simple PK
    matter_type = Column(String)
    sector = Column(String)
    avg_market_fee = Column(Float)
    avg_market_hours = Column(Float)
