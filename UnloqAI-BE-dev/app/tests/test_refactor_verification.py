import pytest
from app.models.meridian import StrategyKPI, ExternalSignal, StrategyRecommendation
from app.services.meridian.seed_meridian import seed_meridian_story

def test_dynamic_kpi_status(client, db_session):
    """
    Edge Case: Ensure status is based on MATH, not STRING MATCHING.
    """
    # 1. Create a "Product B" that is PERFORMING WELL (Current > Target)
    # If the logic is hardcoded to "Product B = Bad", this test will fail.
    good_kpi = StrategyKPI(
        name="Product B Sales",
        current_value=1.5,  # Higher than target
        target_value=1.0,
        unit="£m",
        objective_id=None # detached for test
    )
    db_session.add(good_kpi)
    db_session.commit()

    response = client.get("/api/v1/meridian/kpis")
    data = response.json()
    
    target = next(k for k in data if k["title"] == "Product B Sales")
    
    # STRICT CHECK: It must be 'on_track' because 1.5 > 1.0
    assert target["status"] == "on_track", f"Failed: KPI was {target['status']} but math dictates 'on_track'"
    assert target["trend"]["direction"] == "up"

def test_dynamic_signal_severity(client, db_session):
    """
    Edge Case: Ensure severity comes from DB, not hardcoded to 'High'.
    """
    # 1. Insert a LOW severity signal
    low_sig = ExternalSignal(
        type="market_update",
        description="Minor fluctuation",
        severity="low" # This column must exist now!
    )
    db_session.add(low_sig)
    db_session.commit()

    response = client.get("/api/v1/meridian/signals")
    data = response.json()
    
    target = next(s for s in data if s["description"] == "Minor fluctuation")
    assert target["severity"] == "low", "Failed: Severity hardcoded to High?"

def test_dynamic_approval_impact(client, db_session):
    """
    Edge Case: Ensure the ROI/Impact on the Ledger matches the specific Decision.
    """
    # 1. Create a Recommendation with a specific WEIRD impact value
    unique_impact = "Save 50k bananas"
    rec = StrategyRecommendation(
        title="Monkey Business",
        status="pending",
        impact_estimate=unique_impact # This column must exist!
    )
    db_session.add(rec)
    db_session.commit()

    # 2. Approve it
    client.post(f"/api/v1/meridian/approvals/{rec.recommendation_id}/action", json={"action": "approve"})

    # 3. Check Ledger
    ledger_res = client.get("/api/v1/meridian/ledger")
    entries = ledger_res.json()
    
    # 4. Verify the Ledger entry inherited the "50k bananas"
    entry = next(e for e in entries if e["event"] == "Monkey Business")
    assert entry["impact"] == unique_impact, "Failed: Ledger did not inherit dynamic impact from Decision"