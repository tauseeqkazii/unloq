import pytest
import json
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.models.meridian import ChatSession, ChatMessage, StrategyKPI, ExternalSignal
from app.services.meridian.copilot import CopilotService
from app.services.llm_service import llm_service

# --- CONFIGURATION ---
# Force Ollama for local testing unless Bedrock env vars are explicitly set
if not os.getenv("AWS_ACCESS_KEY_ID"):
    os.environ["LLM_PROVIDER"] = "ollama"
    if not os.getenv("LLM_MODEL"):
        os.environ["LLM_MODEL"] = "llama3.2:1b"

def validate_block_structure(response_json):
    """
    AI RESPONSE ANALYZER:
    Strictly validates that the LLM returned the 'Block' architecture 
    required by the Frontend BlockRenderer.
    """
    assert "type" in response_json, "Missing 'type' field"
    
    # Robust check handling potential whitespace from smaller models
    assert response_json["type"].strip() == "analysis_response", f"Wrong response type: {response_json['type']}"
    
    assert "blocks" in response_json, "Missing 'blocks' array"
    assert isinstance(response_json["blocks"], list), "'blocks' must be a list"
    
    valid_types = ["summary", "metrics", "chart", "recommendation"]
    for block in response_json["blocks"]:
        assert "type" in block, "Block missing 'type'"
        block_type = block["type"].strip()
        assert block_type in valid_types, f"Invalid block type: {block_type}"
        if block_type == "metrics":
            assert "items" in block, "Metrics block missing 'items'"

@pytest.fixture(scope="module")
def seeded_db(db_session):
    """
    Ensures the DB has the specific 'Product B' story for the LLM to find.
    """
    db_session.query(ChatMessage).delete()
    db_session.query(ChatSession).delete()
    
    # Seed 'Product B' Truth
    kpi = db_session.query(StrategyKPI).filter_by(name="Product B Sales").first()
    if not kpi:
        kpi = StrategyKPI(name="Product B Sales", current_value=0.82, target_value=1.08, unit="£m")
        db_session.add(kpi)
    else:
        kpi.current_value = 0.82 
        
    db_session.commit()
    return db_session

def test_01_session_lifecycle(client):
    """Verifies we can Create -> List -> Get History."""
    res = client.post("/api/v1/sessions", json={"title": "Integration Test"})
    assert res.status_code == 200
    session_id = res.json()["session_id"]
    
    res = client.get("/api/v1/sessions")
    assert len(res.json()) > 0
    assert res.json()[0]["session_id"] == session_id
    
    res = client.get(f"/api/v1/sessions/{session_id}/messages")
    assert res.json() == []
    
    return session_id

def test_02_copilot_real_data(client, seeded_db):
    """Validates that the system retrieves real data and LLM formats it correctly."""
    res = client.post("/api/v1/sessions", json={"title": "Data Test"})
    sid = res.json()["session_id"]
    
    query = "Show me the trend for Product B."
    print(f"\n🧠 Asking LLM: '{query}'...")
    
    response = client.post(f"/api/v1/sessions/{sid}/message", json={"content": query})
    assert response.status_code == 200
    
    try:
        data = json.loads(response.text)
        validate_block_structure(data)
        content_dump = json.dumps(data).lower()

        # A. Fact Check (Must match Seeded DB 0.82)
        assert any(x in content_dump for x in ["0.82", "820k", "820,000"]), \
            f"❌ FACT FAIL: LLM did not cite the real value (0.82). Got: {content_dump[:200]}"

        # B. Sentiment Check (Synonyms for 'Down')
        negative_words = ["off track", "down", "decline", "decreased", "drop", "below", "negative", "lower", "struggling"]
        assert any(w in content_dump for w in negative_words), \
            f"❌ SENTIMENT FAIL: Analyzed logic did not indicate negative trend. Got: {content_dump[:200]}"

        # C. Chart Data Integrity
        chart = next((b for b in data['blocks'] if b['type'] == 'chart'), None)
        if chart:
            data_points = chart.get('data', [])
            assert len(data_points) > 0, "❌ DATA FAIL: Chart data is empty."
        
        print("✅ PASS: Real DB history successfully piped to LLM response.")

    except json.JSONDecodeError:
        pytest.fail(f"❌ JSON FAIL: {response.text[:100]}")

def test_03_multi_turn_context(client, seeded_db):
    """Verifies memory."""
    res = client.post("/api/v1/sessions", json={"title": "Memory Test"})
    sid = res.json()["session_id"]
    
    client.post(f"/api/v1/sessions/{sid}/message", json={"content": "My favorite competitor is Competitor X."})
    
    query = "Which competitor did I just mention?"
    res = client.post(f"/api/v1/sessions/{sid}/message", json={"content": query})
    ans = res.text.lower()
    
    assert "competitor x" in ans, "❌ MEMORY FAIL: LLM forgot the previous message."

def test_04_unknown_data_handling(client, seeded_db):
    """Ensure Copilot admits ignorance for missing data."""
    res = client.post("/api/v1/sessions", json={"title": "Test 4"})
    sid = res.json()["session_id"]
    
    query = "How is Product Z performing?"
    response = client.post(f"/api/v1/sessions/{sid}/message", json={"content": query})
    full_text = response.text.lower()
    
    assert "0.82" not in full_text
    denial_phrases = ["no data", "unable to", "don't have", "not found", "cannot", "sorry", "unavailable"]
    assert any(p in full_text for p in denial_phrases), \
        "❌ HALLUCINATION: AI invented an answer instead of admitting no data."

def test_05_api_resilience(client, monkeypatch):
    """Simulate LLM crashing."""
    def mock_stream(*args, **kwargs):
        yield json.dumps({"type": "error", "blocks": [{"type": "summary", "text": "Simulated Crash"}]})
    
    from app.services.llm_service import llm_service
    monkeypatch.setattr(llm_service, "stream_chat", mock_stream)
    
    res = client.post("/api/v1/sessions", json={"title": "Crash Test"})
    sid = res.json()["session_id"]
    response = client.post(f"/api/v1/sessions/{sid}/message", json={"content": "Hello"})
    
    assert response.status_code == 200
    assert "crash" in response.text.lower()