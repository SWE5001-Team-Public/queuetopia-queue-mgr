from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import CreateStore, EditStore, EditStoreStatus
from db.models import StoreTable


async def create_store(db: AsyncSession, store: CreateStore):
  db_store = StoreTable(
    id=store.id,
    s_id=store.s_id,
    name=store.name,
    alias=store.alias,
    company_id=store.company_id
  )
  db.add(db_store)
  await db.commit()
  await db.refresh(db_store)
  return db_store


async def edit_store(db: AsyncSession, store: EditStore):
  """Edit the name and alias of a store by its ID."""
  result = await db.execute(select(StoreTable).filter(StoreTable.id == store.id))
  db_store = result.scalars().first()

  if db_store is None:
    return None

  db_store.name = store.name
  db_store.alias = store.alias

  await db.commit()
  await db.refresh(db_store)

  return db_store


async def edit_store_status(db: AsyncSession, store: EditStoreStatus):
  """Edit the status of a store by its ID."""
  result = await db.execute(select(StoreTable).filter(StoreTable.id == store.id))
  db_store = result.scalars().first()

  if db_store is None:
    return None

  db_store.deactivated = store.deactivated

  await db.commit()
  await db.refresh(db_store)

  return db_store
