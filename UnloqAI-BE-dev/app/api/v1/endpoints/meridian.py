from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from app.db.session import get_db

# Correct — seed_meridian lives under services/oakfield
from app.services.oakfield.seed_meridian import seed_meridian_story

# These are fine (models exist in models/)
from app.models.meridian import (
    StrategyKPI,
    ExternalSignal,
    StrategyRecommendation,
    ImpactLedgerStrategy,
    StrategyOS,
    ChatMessage,
)

# FIXED — these live under services/oakfield
from app.services.oakfield.copilot import CopilotService
from app.services.oakfield.dashboard import DashboardService

# Schemas (assuming schemas/meridian.py exists)
from app.schemas.meridian import (
    KPIResponse,
    SignalResponse,
    RecommendationResponse,
    LedgerEntryResponse,
    ChartDataPoint,
)


router = APIRouter()

class ChatRequest(BaseModel):
    messages: List[dict]

class ApprovalAction(BaseModel):
    action: str # 'approve', 'reject'

class SimulationRequest(BaseModel):
    event_type: str # 'competitor_launch', 'regulation'

@router.get("/chat/history")
def get_chat_history(db: Session = Depends(get_db)):
    msgs = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
    # Map to Vercel Message format
    return [{"id": str(m.id), "role": m.role, "content": m.content} for m in msgs]

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Endpoint /chat hit. Messages: {len(request.messages)}")
    service = CopilotService(db)
    
    return StreamingResponse(
        service.chat_completion(request.messages),
        media_type="text/plain"
    )

@router.get("/kpis", response_model=List[KPIResponse])
def get_kpis(db: Session = Depends(get_db)):
    kpis = db.query(StrategyKPI).all()
    result = []
    for k in kpis:
        # Dynamic Logic: Calculate status based on data
        if k.current_value < k.target_value:
            # If current is less than target, is that bad? Usually yes for Revenue/NPS.
            # Simple assumption: Higher is better.
            deviation = (k.target_value - k.current_value) / k.target_value
            if deviation > 0.15: # 15% miss
                status = "off_track"
            else:
                status = "at_risk"
            trend_direction = "down"
        else:
            status = "on_track"
            trend_direction = "up"
        
        # Hardcoding removed. Using simulated deviation for trend value if not in DB, 
        # but direction is now math-based.
        result.append({
            "title": k.name,
            "value": k.current_value,
            "unit": k.unit,
            "trend": {
                "value": abs(k.current_value - k.target_value), 
                "direction": trend_direction
            },
            "status": status
        })
    return result

@router.get("/signals", response_model=List[SignalResponse])
def get_signals(db: Session = Depends(get_db)):
    signals = db.query(ExternalSignal).order_by(ExternalSignal.timestamp.desc()).all()
    result = []
    for s in signals:
        result.append({
            "id": str(s.signal_id),
            "type": "competitor" if "competitor" in s.type else "market",
            "title": s.type.replace("_", " ").title(),
            "description": s.description,
            "timestamp": s.timestamp.strftime("%H:%M %p"),
            # Dynamic: Use DB column, default to medium if missing
            "severity": getattr(s, "severity", "medium") 
        })
    return result

@router.get("/approvals", response_model=List[RecommendationResponse])
def get_approvals(db: Session = Depends(get_db)):
    recs = db.query(StrategyRecommendation).filter(StrategyRecommendation.status == "pending").all()
    result = []
    for r in recs:
        # Dynamic: Use DB column.
        impact = getattr(r, "impact_estimate", "Impact analysis pending")
        
        result.append({
            "id": str(r.recommendation_id),
            "title": r.title,
            "rationale": r.rationale,
            "status": r.status,
            "impact_estimate": impact
        })
    return result

@router.post("/approvals/{rec_id}/action")
def action_approval(rec_id: str, payload: dict, db: Session = Depends(get_db)):
    """
    Execute an approval action. 
    Handles both real UUIDs from DB and 'hallucinated' demo IDs from LLM.
    """
    action = payload.get("action")
    
    # 1. Try to treat it as a real UUID
    try:
        real_uuid = uuid.UUID(rec_id)
        rec = db.query(StrategyRecommendation).filter(StrategyRecommendation.recommendation_id == real_uuid).first()
        
        if rec:
            rec.status = "approved" if action == "approve" else "rejected"
            
            # Create Ledger Entry if approved
            if action == "approve" and rec.impact_estimate:
                from app.models.meridian import ImpactLedger
                ledger = ImpactLedger(
                    event=f"Approved: {rec.title}",
                    impact_value=rec.impact_estimate,
                    status="Pending",
                    confidence="High"
                )
                db.add(ledger)
            
            db.commit()
            return {"status": "success", "rec_id": str(real_uuid), "new_status": rec.status}

    except ValueError:
        # 2. Fallback: It's a demo/string ID (e.g., "approve_product_b")
        # We simulate success so the demo doesn't crash.
        print(f"⚠️ Handled demo action for non-UUID: {rec_id}")
        return {
            "status": "success", 
            "rec_id": rec_id, 
            "new_status": "approved" if action == "approve" else "rejected",
            "note": "Simulation mode (ID was not a UUID)"
        }

    raise HTTPException(status_code=404, detail="Recommendation not found")

@router.get("/ledger", response_model=List[LedgerEntryResponse])
def get_ledger(db: Session = Depends(get_db)):
    entries = db.query(ImpactLedgerStrategy).all()
    result = []
    for e in entries:
        # Fetch related recommendation title
        title = e.recommendation.title if e.recommendation else "Strategic Action"
        result.append({
            "id": str(e.ledger_id),
            "date": "Today", # Simplified
            "event": title,
            "impact": e.expected_roi,
            "status": "Realized"
        })
    return result

@router.get("/analytics/roi", response_model=List[ChartDataPoint])
def get_roi_chart(db: Session = Depends(get_db)):
    # Mock data for chart
    return [
        {"name": "Jan", "investment": 4000, "return_value": 2400},
        {"name": "Feb", "investment": 3000, "return_value": 1398},
        {"name": "Mar", "investment": 2000, "return_value": 9800},
        {"name": "Apr", "investment": 2780, "return_value": 3908},
        {"name": "May", "investment": 1890, "return_value": 4800},
        {"name": "Jun", "investment": 2390, "return_value": 3800},
    ]

@router.post("/strategy/upload")
async def upload_strategy(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Mock processing
    return {"status": "success", "message": f"Strategy {file.filename} ingested", "objectives_count": 5}

@router.post("/simulation/trigger")
def trigger_simulation(sim: SimulationRequest, db: Session = Depends(get_db)):
    # Create fake signal
    signal = ExternalSignal(
        type=sim.event_type,
        description=f"Simulated Event: {sim.event_type} detected.",
        source_url="http://news.example.com",
        timestamp=datetime.utcnow()
    )
    db.add(signal)
    db.commit() # Commit to get ID
    
    # Create linked recommendation
    rec = StrategyRecommendation(
        trigger_signal_id=signal.signal_id,
        title=f"Response to {sim.event_type}",
        rationale=f"AI Analysis detects high risk from {sim.event_type}. Recommended immediate counter-strategy.",
        status="pending"
    )
    db.add(rec)
    db.commit()
    
    return {"status": "triggered", "signal_id": str(signal.signal_id), "recommendation_id": str(rec.recommendation_id)}


@router.post("/seed")
def run_seed(db: Session = Depends(get_db)):
    seed_meridian_story(db)
    return {"status": "seeded", "message": "Truth Table populated."}


@router.get("/dashboard")
def get_dashboard_composite(db: Session = Depends(get_db)):
    """
    Real composite aggregator. Queries the seeded database.
    """
    service = DashboardService(db)
    return service.get_cockpit_data()