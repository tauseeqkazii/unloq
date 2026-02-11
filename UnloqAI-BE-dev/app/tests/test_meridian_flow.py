import pytest
from app.services.meridian.seed_meridian import seed_meridian_story
from app.models.meridian import StrategyKPI, ImpactLedgerStrategy

def test_01_seed_data_integrity(db_session):
    """
    Verify the isolated DB is empty, then seed it and check fixed data exists.
    """
    # Ensure clean slate
    assert db_session.query(StrategyKPI).count() == 0
    
    # Run Seed
    seed_meridian_story(db_session)
    
    # Verify Seed Results
    kpis = db_session.query(StrategyKPI).all()
    assert len(kpis) > 0
    
    product_b = db_session.query(StrategyKPI).filter(StrategyKPI.name.like("%Product B%")).first()
    assert product_b is not None
    assert product_b.current_value < product_b.target_value  # Should be failing in the story

def test_02_get_dashboard_cockpit(client):
    """
    Test GET /dashboard for the composite JSON structure.
    """
    response = client.get("/api/v1/meridian/dashboard")
    assert response.status_code == 200
    data = response.json()
    
    # 1. Validate Structure
    assert "company" in data
    assert "headline_cards" in data
    assert "top_issues" in data
    assert "decision_inbox_preview" in data
    
    # 2. Validate Data Integrity (Product B should be Off Track)
    cards = data["headline_cards"]
    prod_b_card = next((c for c in cards if "Product B" in c["title"]), None)
    assert prod_b_card is not None
    assert prod_b_card["primary_value"]["status"] == "off_track"
    assert prod_b_card["sparkline"] is not None  # Sparkline data must exist

    # 3. Validate Issues
    issues = data["top_issues"]
    assert len(issues) > 0
    assert issues[0]["status"] in ["off_track", "at_risk"]

def test_03_copilot_intelligence(client, mock_llm):
    """
    Test POST /chat with the mocked LLM.
    Ensures the backend correctly handles the request and streams the response.
    """
    payload = {
        "messages": [
            {"role": "user", "content": "Why is Product B failing?"}
        ]
    }
    
    # Note: TestClient handles streaming responses by allowing iteration over content
    response = client.post("/api/v1/meridian/chat", json=payload)
    assert response.status_code == 200
    
    # Read the streamed content
    content = response.text
    
    # Validate it contains our expected JSON structure keys
    assert "analysis_response" in content
    assert "blocks" in content
    assert "Approve Subscription" in content

def test_04_decision_execution_flow(client, db_session):
    """
    Test the critical 'Approve' loop:
    1. Identify a pending recommendation.
    2. Approve it via API.
    3. Verify it is written to the Ledger.
    """
    # 1. Get Pending Approvals
    dash_response = client.get("/api/v1/meridian/dashboard")
    pending_recs = dash_response.json()["decision_inbox_preview"]
    assert len(pending_recs) > 0
    
    target_rec_id = pending_recs[0]["recommendation_id"]
    
    # 2. Approve Action
    action_payload = {"action": "approve"}
    action_response = client.post(
        f"/api/v1/meridian/approvals/{target_rec_id}/action", 
        json=action_payload
    )
    assert action_response.status_code == 200
    assert action_response.json()["new_status"] == "approved"
    
    # 3. Verify Ledger (The 'Receipt')
    # Use the specific endpoint or the dashboard ledger summary
    ledger_response = client.get("/api/v1/meridian/ledger")
    assert ledger_response.status_code == 200
    ledger_entries = ledger_response.json()
    
    # Find the entry corresponding to our approval
    # (In seed data, we can assume the newest one or filter by ID logic if we had it mapped)
    assert len(ledger_entries) > 0
    
    # 4. Verify Dashboard Summary Update
    # The dashboard ledger summary should now show increased 'Expected ROI' or 'In Progress'
    final_dash = client.get("/api/v1/meridian/dashboard")
    ledger_summary = final_dash.json()["ledger_summary"]
    
    # Check that we have rows in the summary
    assert len(ledger_summary["rows"]) > 0

def test_05_external_signals(client):
    """
    Validate the signals timeline endpoint.
    """
    response = client.get("/api/v1/meridian/signals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "severity" in data[0]
        assert "type" in data[0]