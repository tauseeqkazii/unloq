import pytest
from app.models.meridian import ChatSession, ChatMessage
from app.services.meridian.copilot import CopilotService

def test_multichat_flow(client, db_session):
    # 1. Create Session A (Product B Analysis)
    res_a = client.post("/api/v1/sessions", json={"title": "Product B Analysis"})
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert "session_id" in data_a
    session_a_id = data_a["session_id"]

    # 2. Create Session B (HR Policy)
    res_b = client.post("/api/v1/sessions", json={"title": "HR Policy"})
    assert res_b.status_code == 200
    session_b_id = res_b.json()["session_id"]

    # 3. Send Message to Session A
    msg_a = {"content": "Why is sales down?"}
    client.post(f"/api/v1/sessions/{session_a_id}/message", json=msg_a)

    # 4. Send Message to Session B
    msg_b = {"content": "What is the holiday allowance?"}
    client.post(f"/api/v1/sessions/{session_b_id}/message", json=msg_b)

    # 5. STRICT CHECK: Verify Separation of Concerns
    # Get History A
    hist_a = client.get(f"/api/v1/sessions/{session_a_id}/messages").json()
    # Get History B
    hist_b = client.get(f"/api/v1/sessions/{session_b_id}/messages").json()

    # The messages must NOT leak across sessions
    # Expect: 2 messages (User + assistant) in each, assuming assistant responds.
    # Note: If LLM service is mocked or simple, it might respond. 
    # The previous integration tests passed, so LLM mocks or actual calls are working.
    
    assert len(hist_a) >= 2, f"History A missing messages: {hist_a}"  # User + Assistant
    assert len(hist_b) >= 2, f"History B missing messages: {hist_b}" # User + Assistant
    
    # Check content to ensure they are distinct
    # Flatten content to search easily
    content_a = " ".join([m["content"] for m in hist_a])
    content_b = " ".join([m["content"] for m in hist_b])

    assert "sales" in content_a.lower(), "Session A lost context about sales"
    assert "holiday" in content_b.lower(), "Session B lost context about holiday"
    
    # Ensure no leakage
    assert "holiday" not in content_a.lower(), "Session A leaking content from B"
    assert "sales" not in content_b.lower(), "Session B leaking content from A"

    print("Multi-chat isolation verified.")
