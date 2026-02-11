from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import get_db
from app.schemas import shared as schemas
from app.models import shared as models
from app.crud.base import CRUDBase

company_crud = CRUDBase[models.Company, schemas.CompanyCreate, schemas.CompanyUpdate](models.Company)
decision_crud = CRUDBase[models.Decision, schemas.DecisionCreate, schemas.DecisionUpdate](models.Decision)

companies_router = APIRouter()

@companies_router.get("/", response_model=List[schemas.CompanyResponse])
def read_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    return company_crud.get_multi(db, skip=skip, limit=limit)

@companies_router.post("/", response_model=schemas.CompanyResponse)
def create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db),
):
    return company_crud.create(db, obj_in=company)

@companies_router.get("/{company_id}", response_model=schemas.CompanyResponse)
def read_company(
    company_id: str,
    db: Session = Depends(get_db),
):
    company = company_crud.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# Decisions Router
decisions_router = APIRouter()

@decisions_router.get("/", response_model=List[schemas.DecisionResponse])
def read_decisions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    company_id: str = Query(None),
    status: str = Query(None),
    flow_type: str = Query(None),
):
    filters = {}
    if company_id: filters['company_id'] = company_id
    if status: filters['status'] = status
    if flow_type: filters['flow_type'] = flow_type
    
    return decision_crud.get_multi(db, skip=skip, limit=limit, filters=filters)

@decisions_router.post("/", response_model=schemas.DecisionResponse)
def create_decision(
    decision: schemas.DecisionCreate,
    db: Session = Depends(get_db),
):
    return decision_crud.create(db, obj_in=decision)

@decisions_router.get("/{decision_id}", response_model=schemas.DecisionResponse)
def read_decision(
    decision_id: str,
    db: Session = Depends(get_db),
):
    decision = decision_crud.get(db, id=decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision
