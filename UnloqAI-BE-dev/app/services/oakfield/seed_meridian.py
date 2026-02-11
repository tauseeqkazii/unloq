from sqlalchemy.orm import Session
from app.models.meridian import StrategyOS, StrategyObjective, StrategyKPI, InternalSignal, ExternalSignal, StrategyRecommendation, ImpactLedgerStrategy
from datetime import datetime, timedelta
import uuid

def seed_meridian_story(db: Session):
    """
    Seeds a deterministic, board-grade scenario.
    NO RANDOMNESS in the API. All history is physically inserted here.
    """
    # 1. Clear existing Meridian data
    # (Cascades should handle children, but being explicit is safer)
    db.query(StrategyOS).delete()
    db.query(ExternalSignal).delete()
    db.commit()

    # 2. Strategy Shell
    strat = StrategyOS(version="2026-Q1", period_start=datetime(2026, 1, 1), period_end=datetime(2026, 12, 31))
    db.add(strat)
    db.flush()

    obj_growth = StrategyObjective(strategy_id=strat.strategy_id, text="Accelerate Revenue Growth", status="at_risk", owner_role="CRO")
    db.add(obj_growth)
    db.flush()

    # 3. KPI: Product B (The "Problem" Child)
    # Target: 1.2m, Current: 0.82m (Failing)
    kpi_prod_b = StrategyKPI(
        objective_id=obj_growth.objective_id,
        name="Product B Sales",
        target_value=1.20,
        current_value=0.82,
        unit="£m"
    )
    db.add(kpi_prod_b)
    db.flush()

    # --- CRITICAL: GENERATE PHYSICAL HISTORY ---
    # We create 90 real rows in the DB so the chart tool works without simulation.
    # Scenario: Smooth decline from 1.1m down to 0.82m over 90 days.
    start_val = 1.10
    end_val = 0.82
    days = 90
    
    for i in range(days):
        # Calculate exact value for this day (Linear interpolation)
        # Day 0 = 90 days ago. Day 89 = Today.
        progress = i / days
        current_daily_val = start_val - ((start_val - end_val) * progress)
        
        # Timestamp: 90 days ago + i days
        ts = datetime.utcnow() - timedelta(days=(days - i))
        
        signal = InternalSignal(
            kpi_id=kpi_prod_b.kpi_id,
            timestamp=ts,
            value=round(current_daily_val, 3),
            source_system="ERP_Finance"
        )
        db.add(signal)

    # 4. External Signals (RAG Context)
    ext_sig = ExternalSignal(
        type="competitor_launch",
        description="Competitor X launched 'Nova' platform at 30% lower price point, impacting mid-market segment.",
        source_url="market_intel_report_2025.pdf",
        severity="high", # Enforced schema
        timestamp=datetime.utcnow() - timedelta(days=15)
    )
    db.add(ext_sig)

    # 5. Recommendation (The Action)
    rec = StrategyRecommendation(
        trigger_signal_id=ext_sig.signal_id,
        title="Reposition Product B",
        rationale="Shift value proposition to Enterprise tier to avoid price war with Competitor X.",
        status="pending",
        impact_estimate="£1.2m"
    )
    db.add(rec)

    db.commit()
    print("✅ Meridian Seeded: 90 Days of physical history created.")