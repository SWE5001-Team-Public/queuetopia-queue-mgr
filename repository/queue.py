from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import QueueTable
from schemas import CreateQueue


async def create_queue(db: AsyncSession, queue: CreateQueue):
  """Create a new queue."""
  db_queue = QueueTable(
    queue_type=queue.queue_type,
    store_id=queue.store_id,
  )
  db.add(db_queue)
  await db.commit()
  await db.refresh(db_queue)
  return db_queue


async def get_queue_by_store_id_and_queue_type(db: AsyncSession, queue: CreateQueue):
  """Retrieve a queue by store ID & queue type."""
  result = await db.execute(
    select(QueueTable).filter(QueueTable.queue_type == queue.queue_type, QueueTable.store_id == queue.store_id))
  return result.scalar_one_or_none()
