from pydantic import BaseModel
from humps import camelize


def to_camel(string: str) -> str:
  return camelize(string)


class CreateStore(BaseModel):
  id: str
  s_id: int
  name: str
  alias: str | None
  company_id: str


class EditStore(BaseModel):
  id: str
  name: str
  alias: str | None


class EditStoreStatus(BaseModel):
  id: str
  deactivated: bool
