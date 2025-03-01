from sqlalchemy import Column, String, Integer, Boolean
import uuid

from sqlalchemy.ext.hybrid import hybrid_property

from db.database import Base


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
