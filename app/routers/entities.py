from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/entities",
    tags=["entities"],
)

@router.get("/", response_model=List[schemas.Entity])
def read_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entities = crud.get_entities(db, skip=skip, limit=limit)
    return entities

@router.post("/", response_model=schemas.Entity)
def create_new_entity(entity: schemas.EntityCreate, db: Session = Depends(get_db)):
    db_entity = crud.get_entity(db, entity_id=entity.entity_id)
    if db_entity:
        raise HTTPException(status_code=400, detail="Entity already exists")
    return crud.create_entity(db=db, entity=entity)

@router.get("/{entity_id}", response_model=schemas.Entity)
def read_entity(entity_id: int, db: Session = Depends(get_db)):
    db_entity = crud.get_entity(db, entity_id=entity_id)
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity

@router.put("/{entity_id}", response_model=schemas.Entity)
def update_existing_entity(entity_id: int, entity_update: schemas.EntityBase, db: Session = Depends(get_db)):
    updated_entity = crud.update_entity(db, entity_id=entity_id, entity_update=entity_update)
    if updated_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return updated_entity

@router.delete("/{entity_id}", response_model=schemas.Entity)
def delete_existing_entity(entity_id: int, db: Session = Depends(get_db)):
    deleted_entity = crud.delete_entity(db, entity_id=entity_id)
    if deleted_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return deleted_entity
