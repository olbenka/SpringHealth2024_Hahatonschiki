from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Numeric, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from .database import Base

# Ассоциативная таблица для связи между спринтами и задачами
sprint_entity_association = Table(
    'sprint_entity_association',
    Base.metadata,
    Column('sprint_id', Integer, ForeignKey('sprints.sprint_id', ondelete='CASCADE')),
    Column('entity_id', BigInteger, ForeignKey('entities.entity_id', ondelete='CASCADE'))
)

class Entity(Base):
    __tablename__ = 'entities'

    entity_id = Column(BigInteger, primary_key=True, index=True)
    area = Column(String(255))
    type = Column(String(255))
    status = Column(String(255))
    priority = Column(String(255))
    ticket_number = Column(String(255))
    create_date = Column(DateTime)
    update_date = Column(DateTime)
    estimation = Column(Numeric)
    spent = Column(Numeric)
    resolution = Column(String(255))

    # Связь с историей
    histories = relationship("History", back_populates="entity")

    # Связь с спринтами
    sprints = relationship("Sprint", secondary=sprint_entity_association, back_populates="entities")

class History(Base):
    __tablename__ = 'history'

    history_id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(BigInteger, ForeignKey('entities.entity_id', ondelete='CASCADE'))
    history_property_name = Column(String(255))
    history_date = Column(DateTime)
    history_version = Column(Integer)
    history_change_type = Column(String(255))
    history_change = Column(Text)

    # Связь с задачами
    entity = relationship("Entity", back_populates="histories")

class Sprint(Base):
    __tablename__ = 'sprints'

    sprint_id = Column(Integer, primary_key=True, index=True)
    sprint_name = Column(String(255))
    sprint_status = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Связь с задачами
    entities = relationship("Entity", secondary=sprint_entity_association, back_populates="sprints")
