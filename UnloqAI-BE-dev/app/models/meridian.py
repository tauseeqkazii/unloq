import uuid
from datetime import datetime
from typing import Any, List
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class StrategyOS(Base):
    __tablename__ = "strategy_os"

    strategy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    version = Column(String)
    raw_doc_path = Column(String)

    objectives = relationship("StrategyObjective", back_populates="strategy", cascade="all, delete-orphan")

class StrategyObjective(Base):
    __tablename__ = "strategy_objectives"

    objective_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategy_os.strategy_id"))
    text = Column(String)
    owner_role = Column(String)
    status = Column(String)  # 'on_track', 'at_risk'

    strategy = relationship("StrategyOS", back_populates="objectives")
    kpis = relationship("StrategyKPI", back_populates="objective", cascade="all, delete-orphan")

class StrategyKPI(Base):
    __tablename__ = "strategy_kpis"

    kpi_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    objective_id = Column(UUID(as_uuid=True), ForeignKey("strategy_objectives.objective_id"))
    name = Column(String)
    target_value = Column(Float)
    current_value = Column(Float)
    unit = Column(String)

    objective = relationship("StrategyObjective", back_populates="kpis")

class InternalSignal(Base):
    __tablename__ = "internal_signals"

    signal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("strategy_kpis.kpi_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    value = Column(Float)
    source_system = Column(String)

class ExternalSignal(Base):
    __tablename__ = "external_signals"

    signal_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String)  # 'competitor_launch', 'regulation'
    description = Column(String)
    source_url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Vector(1536))
    # ADDED: Store severity in DB
    severity = Column(String, default="medium")

class StrategyRecommendation(Base):
    __tablename__ = "strategy_recommendations"

    recommendation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Trigger can be from external or internal signal, making FK optional or loose. 
    # For strict schema, we might usually separate, but for demo we can link to external primarily 
    # or just store ID as string if polymorphic.
    # Let's link to ExternalSignal for now as per "Trigger: Competitor X Launch" example.
    trigger_signal_id = Column(UUID(as_uuid=True), ForeignKey("external_signals.signal_id"), nullable=True) 
    title = Column(String)
    rationale = Column(Text)
    status = Column(String)  # 'pending', 'approved', 'rejected'
    # ADDED: Store the impact estimate in DB
    impact_estimate = Column(String)

class ImpactLedgerStrategy(Base):
    __tablename__ = "impact_ledger_strategy"

    ledger_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("strategy_recommendations.recommendation_id"))
    expected_roi = Column(String)
    actual_roi = Column(String)
    kpi_impacted = Column(String)

    recommendation = relationship("StrategyRecommendation")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True) # Link to user
    title = Column(String, default="New Conversation") # "Analysis of Product B"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id"), nullable=False)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
