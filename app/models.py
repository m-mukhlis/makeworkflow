from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True)
    devops_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    current_state = Column(String)
    last_updated = Column(DateTime)

    # TODO: You might need additional models...
    transitions = relationship("StateTransition", back_populates="work_item")


class StateTransition(Base):
    __tablename__ = "state_transitions"

    id = Column(Integer, primary_key=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False)
    from_state = Column(String, nullable=False)
    to_state = Column(String, nullable=False)
    changed_by = Column(String, nullable=True)
    changed_at = Column(DateTime, nullable=False)
    recorded_at = Column(DateTime)

    work_item = relationship("WorkItem", back_populates="transitions")