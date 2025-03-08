from humps import camelize
from pydantic import BaseModel


def to_camel(string: str) -> str:
  return camelize(string)


class QueueTypeResponse(BaseModel):
  key: str
  value: str


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


class CreateQueue(BaseModel):
  queue_type: str
  store_id: str
