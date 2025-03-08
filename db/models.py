from sqlalchemy import Column, String, Integer, Boolean
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
