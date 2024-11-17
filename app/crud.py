from sqlalchemy.orm import Session
from . import models, schemas

# CRUD операции для Entity
def get_entity(db: Session, entity_id: int):
    return db.query(models.Entity).filter(models.Entity.entity_id == entity_id).first()

def get_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Entity).offset(skip).limit(limit).all()

def create_entity(db: Session, entity: schemas.EntityCreate):
    db_entity = models.Entity(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

def update_entity(db: Session, entity_id: int, entity_update: schemas.EntityBase):
    db_entity = get_entity(db, entity_id)
    if not db_entity:
        return None
    update_data = entity_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entity, key, value)
    db.commit()
    db.refresh(db_entity)
    return db_entity

def delete_entity(db: Session, entity_id: int):
    db_entity = get_entity(db, entity_id)
    if not db_entity:
        return None
    db.delete(db_entity)
    db.commit()
    return db_entity

# CRUD операции для History
def get_history(db: Session, history_id: int):
    return db.query(models.History).filter(models.History.history_id == history_id).first()

def get_histories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.History).offset(skip).limit(limit).all()

def get_histories_by_entity(db: Session, entity_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.History).filter(models.History.entity_id == entity_id).offset(skip).limit(limit).all()

def create_history(db: Session, history: schemas.HistoryCreate):
    db_history = models.History(**history.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def update_history(db: Session, history_id: int, history_update: schemas.HistoryBase):
    db_history = get_history(db, history_id)
    if not db_history:
        return None
    update_data = history_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_history, key, value)
    db.commit()
    db.refresh(db_history)
    return db_history

def delete_history(db: Session, history_id: int):
    db_history = get_history(db, history_id)
    if not db_history:
        return None
    db.delete(db_history)
    db.commit()
    return db_history

# CRUD операции для Sprint
def get_sprint(db: Session, sprint_id: int):
    return db.query(models.Sprint).filter(models.Sprint.sprint_id == sprint_id).first()

def get_sprints(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sprint).offset(skip).limit(limit).all()

def create_sprint(db: Session, sprint: schemas.SprintCreate):
    db_sprint = models.Sprint(**sprint.dict())
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint

def update_sprint(db: Session, sprint_id: int, sprint_update: schemas.SprintBase):
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return None
    update_data = sprint_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sprint, key, value)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint

def delete_sprint(db: Session, sprint_id: int):
    db_sprint = get_sprint(db, sprint_id)
    if not db_sprint:
        return None
    db.delete(db_sprint)
    db.commit()
    return db_sprint
