from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.session import get_db
from app.schemas import harper as schemas
from app.models import harper as models
from app.crud.base import CRUDBase

contract_crud = CRUDBase[models.HarperContract, schemas.HarperContractCreate, schemas.HarperContractUpdate](models.HarperContract)

router = APIRouter()

@router.get("/contracts", response_model=List[schemas.HarperContractResponse])
def read_contracts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    contract_type: str = Query(None),
    sector: str = Query(None),
    risk_band: str = Query(None),
):
    filters = {}
    if contract_type: filters['contract_type'] = contract_type
    if sector: filters['sector'] = sector
    if risk_band: filters['risk_band'] = risk_band
    
    return contract_crud.get_multi(db, skip=skip, limit=limit, filters=filters)

@router.post("/contracts", response_model=schemas.HarperContractResponse)
def create_contract(
    contract: schemas.HarperContractCreate,
    db: Session = Depends(get_db),
):
    return contract_crud.create(db, obj_in=contract)

@router.get("/contracts/{id}", response_model=schemas.HarperContractResponse)
def read_contract(
    id: str,
    db: Session = Depends(get_db),
):
    item = contract_crud.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    return item

@router.put("/contracts/{id}", response_model=schemas.HarperContractResponse)
def update_contract(
    id: str,
    contract_in: schemas.HarperContractUpdate,
    db: Session = Depends(get_db),
):
    item = contract_crud.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract_crud.update(db, db_obj=item, obj_in=contract_in)
