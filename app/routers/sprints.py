from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from ..calculations import calculate_metrics

router = APIRouter(
    prefix="/sprints",
    tags=["sprints"],
)

@router.get("/", response_model=List[schemas.Sprint])
def read_sprints(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sprints = crud.get_sprints(db, skip=skip, limit=limit)
    return sprints

@router.post("/", response_model=schemas.Sprint)
def create_new_sprint(sprint: schemas.SprintCreate, db: Session = Depends(get_db)):
    return crud.create_sprint(db=db, sprint=sprint)

@router.get("/{sprint_id}", response_model=schemas.Sprint)
def read_sprint(sprint_id: int, db: Session = Depends(get_db)):
    db_sprint = crud.get_sprint(db, sprint_id=sprint_id)
    if db_sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return db_sprint

@router.put("/{sprint_id}", response_model=schemas.Sprint)
def update_existing_sprint(sprint_id: int, sprint_update: schemas.SprintBase, db: Session = Depends(get_db)):
    updated_sprint = crud.update_sprint(db, sprint_id=sprint_id, sprint_update=sprint_update)
    if updated_sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return updated_sprint

@router.delete("/{sprint_id}", response_model=schemas.Sprint)
def delete_existing_sprint(sprint_id: int, db: Session = Depends(get_db)):
    deleted_sprint = crud.delete_sprint(db, sprint_id=sprint_id)
    if deleted_sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return deleted_sprint

@router.get("/{sprint_id}/metrics")
def get_sprint_metrics(sprint_id: int, db: Session = Depends(get_db)):
    metrics = calculate_metrics(db, sprint_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Sprint not found or metrics unavailable")
    return metrics
