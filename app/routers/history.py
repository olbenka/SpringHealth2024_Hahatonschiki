from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/history",
    tags=["history"],
)

@router.get("/", response_model=List[schemas.History])
def read_histories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    histories = crud.get_histories(db, skip=skip, limit=limit)
    return histories

@router.post("/", response_model=schemas.History)
def create_new_history(history: schemas.HistoryCreate, db: Session = Depends(get_db)):
    return crud.create_history(db=db, history=history)

@router.get("/{history_id}", response_model=schemas.History)
def read_history(history_id: int, db: Session = Depends(get_db)):
    db_history = crud.get_history(db, history_id=history_id)
    if db_history is None:
        raise HTTPException(status_code=404, detail="History not found")
    return db_history

@router.put("/{history_id}", response_model=schemas.History)
def update_existing_history(history_id: int, history_update: schemas.HistoryBase, db: Session = Depends(get_db)):
    updated_history = crud.update_history(db, history_id=history_id, history_update=history_update)
    if updated_history is None:
        raise HTTPException(status_code=404, detail="History not found")
    return updated_history

@router.delete("/{history_id}", response_model=schemas.History)
def delete_existing_history(history_id: int, db: Session = Depends(get_db)):
    deleted_history = crud.delete_history(db, history_id=history_id)
    if deleted_history is None:
        raise HTTPException(status_code=404, detail="History not found")
    return deleted_history
