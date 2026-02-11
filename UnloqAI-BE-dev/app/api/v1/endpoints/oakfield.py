from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.oakfield import (
    OakfieldDevelopmentCreate,
    OakfieldDevelopmentUpdate,
    OakfieldDevelopmentResponse,
    OakfieldHouseTypeCreate,
    OakfieldHouseTypeUpdate,
    OakfieldHouseTypeResponse,
    OakfieldOptionCreate,
    OakfieldOptionUpdate,
    OakfieldOptionResponse,
    OakfieldBundleCreate,
    OakfieldBundleUpdate,
    OakfieldBundleResponse,
    OakfieldBundleRuleCreate,
    OakfieldBundleRuleUpdate,
    OakfieldBundleRuleResponse,
    OakfieldOptionBasketCreate,
    OakfieldOptionBasketUpdate,
    OakfieldOptionBasketResponse,
)
from app.models.oakfield import (
    OakfieldDevelopment,
    OakfieldHouseType,
    OakfieldOption,
    OakfieldBundle,
    OakfieldBundleRule,
    OakfieldOptionBasket,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Developments
# ---------------------------------------------------------------------------

@router.get("/developments", response_model=List[OakfieldDevelopmentResponse])
def list_developments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = Query(None),
    character: Optional[str] = Query(None),
):
    query = db.query(OakfieldDevelopment)
    if region:
        query = query.filter(OakfieldDevelopment.region == region)
    if character:
        query = query.filter(OakfieldDevelopment.character == character)
    return query.offset(skip).limit(limit).all()


@router.get("/developments/{dev_code}", response_model=OakfieldDevelopmentResponse)
def get_development(dev_code: str, db: Session = Depends(get_db)):
    item = db.query(OakfieldDevelopment).filter(
        OakfieldDevelopment.dev_code == dev_code
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Development not found")
    return item


@router.post("/developments", response_model=OakfieldDevelopmentResponse)
def create_development(
    payload: OakfieldDevelopmentCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(OakfieldDevelopment).filter(
        OakfieldDevelopment.dev_code == payload.dev_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="dev_code already exists")
    obj = OakfieldDevelopment(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/developments/{dev_code}", response_model=OakfieldDevelopmentResponse)
def update_development(
    dev_code: str,
    payload: OakfieldDevelopmentUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(OakfieldDevelopment).filter(
        OakfieldDevelopment.dev_code == dev_code
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Development not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/developments/{dev_code}")
def delete_development(dev_code: str, db: Session = Depends(get_db)):
    obj = db.query(OakfieldDevelopment).filter(
        OakfieldDevelopment.dev_code == dev_code
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Development not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted", "dev_code": dev_code}


# ---------------------------------------------------------------------------
# House Types
# ---------------------------------------------------------------------------

@router.get("/house-types", response_model=List[OakfieldHouseTypeResponse])
def list_house_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    beds: Optional[int] = Query(None),
):
    query = db.query(OakfieldHouseType)
    if beds is not None:
        query = query.filter(OakfieldHouseType.beds == beds)
    return query.offset(skip).limit(limit).all()


@router.get("/house-types/{id}", response_model=OakfieldHouseTypeResponse)
def get_house_type(id: int, db: Session = Depends(get_db)):
    item = db.query(OakfieldHouseType).filter(OakfieldHouseType.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="House type not found")
    return item


@router.post("/house-types", response_model=OakfieldHouseTypeResponse)
def create_house_type(
    payload: OakfieldHouseTypeCreate,
    db: Session = Depends(get_db),
):
    obj = OakfieldHouseType(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/house-types/{id}", response_model=OakfieldHouseTypeResponse)
def update_house_type(
    id: int,
    payload: OakfieldHouseTypeUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(OakfieldHouseType).filter(OakfieldHouseType.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="House type not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

@router.get("/options", response_model=List[OakfieldOptionResponse])
def list_options(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 200,
    category: Optional[str] = Query(None),
):
    query = db.query(OakfieldOption)
    if category:
        query = query.filter(OakfieldOption.category == category)
    return query.offset(skip).limit(limit).all()


@router.get("/options/{option_code}", response_model=OakfieldOptionResponse)
def get_option(option_code: str, db: Session = Depends(get_db)):
    item = db.query(OakfieldOption).filter(
        OakfieldOption.option_code == option_code
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Option not found")
    return item


@router.post("/options", response_model=OakfieldOptionResponse)
def create_option(
    payload: OakfieldOptionCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(OakfieldOption).filter(
        OakfieldOption.option_code == payload.option_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="option_code already exists")
    obj = OakfieldOption(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/options/{option_code}", response_model=OakfieldOptionResponse)
def update_option(
    option_code: str,
    payload: OakfieldOptionUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(OakfieldOption).filter(
        OakfieldOption.option_code == option_code
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Option not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


# ---------------------------------------------------------------------------
# Bundles
# ---------------------------------------------------------------------------

@router.get("/bundles", response_model=List[OakfieldBundleResponse])
def list_bundles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    return db.query(OakfieldBundle).offset(skip).limit(limit).all()


@router.get("/bundles/{bundle_code}", response_model=OakfieldBundleResponse)
def get_bundle(bundle_code: str, db: Session = Depends(get_db)):
    item = db.query(OakfieldBundle).filter(
        OakfieldBundle.bundle_code == bundle_code
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bundle not found")
    return item


@router.post("/bundles", response_model=OakfieldBundleResponse)
def create_bundle(
    payload: OakfieldBundleCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(OakfieldBundle).filter(
        OakfieldBundle.bundle_code == payload.bundle_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="bundle_code already exists")
    obj = OakfieldBundle(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bundles/{bundle_code}", response_model=OakfieldBundleResponse)
def update_bundle(
    bundle_code: str,
    payload: OakfieldBundleUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(OakfieldBundle).filter(
        OakfieldBundle.bundle_code == bundle_code
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Bundle not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


# ---------------------------------------------------------------------------
# Bundle Rules
# ---------------------------------------------------------------------------

@router.get("/bundle-rules", response_model=List[OakfieldBundleRuleResponse])
def list_bundle_rules(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 200,
    bundle_code: Optional[str] = Query(None),
):
    query = db.query(OakfieldBundleRule)
    if bundle_code:
        query = query.filter(OakfieldBundleRule.bundle_code == bundle_code)
    return query.offset(skip).limit(limit).all()


@router.get("/bundle-rules/{id}", response_model=OakfieldBundleRuleResponse)
def get_bundle_rule(id: int, db: Session = Depends(get_db)):
    item = db.query(OakfieldBundleRule).filter(OakfieldBundleRule.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bundle rule not found")
    return item


@router.post("/bundle-rules", response_model=OakfieldBundleRuleResponse)
def create_bundle_rule(
    payload: OakfieldBundleRuleCreate,
    db: Session = Depends(get_db),
):
    # Verify the referenced bundle exists
    bundle = db.query(OakfieldBundle).filter(
        OakfieldBundle.bundle_code == payload.bundle_code
    ).first()
    if not bundle:
        raise HTTPException(status_code=400, detail="Referenced bundle_code does not exist")
    obj = OakfieldBundleRule(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bundle-rules/{id}", response_model=OakfieldBundleRuleResponse)
def update_bundle_rule(
    id: int,
    payload: OakfieldBundleRuleUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(OakfieldBundleRule).filter(OakfieldBundleRule.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Bundle rule not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/bundle-rules/{id}")
def delete_bundle_rule(id: int, db: Session = Depends(get_db)):
    obj = db.query(OakfieldBundleRule).filter(OakfieldBundleRule.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Bundle rule not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted", "id": id}


# ---------------------------------------------------------------------------
# Option Baskets
# ---------------------------------------------------------------------------

@router.get("/baskets", response_model=List[OakfieldOptionBasketResponse])
def list_baskets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    development_code: Optional[str] = Query(None),
    house_type: Optional[str] = Query(None),
    build_stage: Optional[str] = Query(None),
    character: Optional[str] = Query(None),
):
    query = db.query(OakfieldOptionBasket)
    if development_code:
        query = query.filter(OakfieldOptionBasket.development_code == development_code)
    if house_type:
        query = query.filter(OakfieldOptionBasket.house_type == house_type)
    if build_stage:
        query = query.filter(OakfieldOptionBasket.build_stage == build_stage)
    if character:
        query = query.filter(OakfieldOptionBasket.character == character)
    return query.offset(skip).limit(limit).all()


@router.get("/baskets/{id}", response_model=OakfieldOptionBasketResponse)
def get_basket(id: int, db: Session = Depends(get_db)):
    item = db.query(OakfieldOptionBasket).filter(
        OakfieldOptionBasket.id == id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Basket not found")
    return item


@router.post("/baskets", response_model=OakfieldOptionBasketResponse)
def create_basket(
    payload: OakfieldOptionBasketCreate,
    db: Session = Depends(get_db),
):
    # Validate development_code exists if provided
    if payload.development_code:
        dev = db.query(OakfieldDevelopment).filter(
            OakfieldDevelopment.dev_code == payload.development_code
        ).first()
        if not dev:
            raise HTTPException(
                status_code=400,
                detail=f"development_code '{payload.development_code}' not found"
            )
    obj = OakfieldOptionBasket(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/baskets/{id}", response_model=OakfieldOptionBasketResponse)
def update_basket(
    id: int,
    payload: OakfieldOptionBasketUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(OakfieldOptionBasket).filter(
        OakfieldOptionBasket.id == id
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Basket not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/baskets/{id}")
def delete_basket(id: int, db: Session = Depends(get_db)):
    obj = db.query(OakfieldOptionBasket).filter(
        OakfieldOptionBasket.id == id
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Basket not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted", "id": id}


# ---------------------------------------------------------------------------
# Analytics — basket margin summary per development
# ---------------------------------------------------------------------------

@router.get("/analytics/margin-summary")
def margin_summary(
    db: Session = Depends(get_db),
    development_code: Optional[str] = Query(None),
):
    """
    Returns per-development margin stats derived entirely from
    oakfield_option_baskets and oakfield_developments.
    No legacy tables are touched.
    """
    query = db.query(OakfieldOptionBasket)
    if development_code:
        query = query.filter(OakfieldOptionBasket.development_code == development_code)

    baskets = query.all()

    if not baskets:
        return {"message": "No baskets found", "data": []}

    # Group by development_code
    from collections import defaultdict
    groups: dict = defaultdict(list)
    for b in baskets:
        groups[b.development_code or "UNKNOWN"].append(b)

    result = []
    for dev_code, dev_baskets in groups.items():
        revenues = [b.options_revenue or 0.0 for b in dev_baskets]
        margins = [b.options_margin_percent or 0.0 for b in dev_baskets]
        deltas = [b.margin_delta_percent or 0.0 for b in dev_baskets]
        count = len(dev_baskets)

        below_target = sum(1 for b in dev_baskets if (b.margin_delta_percent or 0.0) < 0)
        bundles_triggered = sum(
            1 for b in dev_baskets
            if b.bundles_triggered and len(b.bundles_triggered) > 0
        )
        bundle_offered = sum(
            1 for b in dev_baskets if b.bundle_offered
        )

        result.append({
            "development_code": dev_code,
            "basket_count": count,
            "avg_options_revenue": round(sum(revenues) / count, 2) if count else 0,
            "avg_margin_percent": round(sum(margins) / count, 2) if count else 0,
            "avg_margin_delta": round(sum(deltas) / count, 2) if count else 0,
            "baskets_below_target": below_target,
            "bundles_triggered_count": bundles_triggered,
            "bundle_offered_count": bundle_offered,
        })

    return {"data": result}


# ---------------------------------------------------------------------------
# Analytics — bundle trigger analysis
# ---------------------------------------------------------------------------

@router.get("/analytics/bundle-opportunities")
def bundle_opportunities(
    db: Session = Depends(get_db),
    development_code: Optional[str] = Query(None),
):
    """
    Identifies baskets where bundle rules were triggered but no bundle was offered.
    Surfacing missed upsell revenue opportunities.
    """
    query = db.query(OakfieldOptionBasket)
    if development_code:
        query = query.filter(OakfieldOptionBasket.development_code == development_code)

    baskets = query.all()
    missed = []

    for b in baskets:
        triggered = b.bundles_triggered or []
        offered = b.bundle_offered

        # Missed opportunity: rules fired but nothing was offered
        if triggered and not offered:
            # Estimate potential revenue from triggered bundles
            total_potential = 0.0
            for bundle_code in triggered:
                bundle = db.query(OakfieldBundle).filter(
                    OakfieldBundle.bundle_code == bundle_code
                ).first()
                if bundle and bundle.additional_revenue:
                    total_potential += bundle.additional_revenue

            missed.append({
                "basket_id": b.id,
                "development_code": b.development_code,
                "plot_reference": b.plot_reference,
                "customer_name": b.customer_name,
                "house_type": b.house_type,
                "build_stage": b.build_stage,
                "triggered_bundles": triggered,
                "estimated_missed_revenue": round(total_potential, 2),
            })

    return {
        "missed_opportunity_count": len(missed),
        "data": missed,
    }


# ---------------------------------------------------------------------------
# Strategist chat endpoint
# ---------------------------------------------------------------------------

class OakfieldChatRequest(BaseModel):
    content: str


@router.post("/strategist/chat")
async def oakfield_strategist_chat(
    req: OakfieldChatRequest,
    db: Session = Depends(get_db),
):
    """
    Streams a structured JSON analysis from the Oakfield Strategist AI.
    Queries only oakfield_* tables. No Meridian dependency.
    """
    from app.services.oakfield.copilot import OakfieldCopilotService
    service = OakfieldCopilotService(db)
    return StreamingResponse(
        service.chat_completion(req.content),
        media_type="text/plain",
    )


# ---------------------------------------------------------------------------
# Bundle eligibility check endpoint
# ---------------------------------------------------------------------------

@router.get("/baskets/{id}/eligibility/{bundle_code}")
def check_basket_bundle_eligibility(
    id: int,
    bundle_code: str,
    db: Session = Depends(get_db),
):
    """
    Evaluates whether a bundle is eligible for a given basket
    based on OakfieldBundleRule constraints (build stage, beds, options, revenue floor).
    """
    from app.services.oakfield.tools import OakfieldTools
    tools = OakfieldTools(db)
    return tools.check_bundle_eligibility(basket_id=id, bundle_code=bundle_code)