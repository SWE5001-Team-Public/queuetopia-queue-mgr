import uuid

from sqlalchemy import Column, String, Integer, Boolean, Sequence, ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from db.base import Base


class StaticTable(Base):
  __tablename__ = 'static'

  key = Column(String(50), primary_key=True, index=True, nullable=False)
  value = Column(String(100), nullable=False)
  type = Column(String(100), nullable=False)


class StoreTable(Base):
  __tablename__ = "stores"

  id = Column(String, primary_key=True, index=True, nullable=False)
  s_id = Column(Integer, index=True, nullable=False)
  name = Column(String, nullable=False)
  alias = Column(String, nullable=True)
  deactivated = Column(Boolean, default=False, nullable=False)
  company_id = Column(String, nullable=False)

  @hybrid_property
  def display_id(self):
    return f"S{self.s_id}"


class QueueTable(Base):
  __tablename__ = "queues"
  __table_args__ = (
    UniqueConstraint("queue_type", "store_id", name="uq_queue_type_store_id"),
  )

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  q_id = Column(Integer, Sequence('queue_q_id_seq'), unique=True, index=True, autoincrement=True, nullable=False)
  queue_type = Column(String(50), ForeignKey("static.key", onupdate="CASCADE"), nullable=False)
  description = Column(String, nullable=True)
  status = Column(String(50), ForeignKey("static.key", onupdate="CASCADE"), nullable=False, default="Closed")
  capacity = Column(Integer, nullable=False, default=0)
  deactivated = Column(Boolean, default=True, nullable=False)
  store_id = Column(String, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)

  @hybrid_property
  def display_id(self):
    return f"Q{self.q_id}"
