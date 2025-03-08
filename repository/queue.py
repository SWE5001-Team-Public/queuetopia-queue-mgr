from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import QueueTable
from schemas import CreateQueue, ModifyQueue, ModifyQueueStatus, ModifyQueueActiveStatus


async def create_queue(db: AsyncSession, queue: CreateQueue):
  """Create a new queue."""
  db_queue = QueueTable(
    queue_type=queue.queue_type,
    description=queue.description,
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


async def get_queues_by_store_id(db: AsyncSession, store_id: str):
  """Retrieve list of queue by store id."""
  result = await db.execute(
    select(QueueTable).filter(QueueTable.store_id == store_id))
  return result.scalars().all()


async def get_queue_by_id(db: AsyncSession, queue_id: str):
  """Retrieve a queue by id."""
  result = await db.execute(select(QueueTable).filter(QueueTable.id == queue_id))
  return result.scalar_one_or_none()


async def edit_queue_details(db: AsyncSession, queue: ModifyQueue):
  """Edit queue details by its ID."""
  result = await db.execute(select(QueueTable).filter(QueueTable.id == queue.id))
  db_queue = result.scalars().first()

  if db_queue is None:
    return None

  db_queue.queue_type = queue.queue_type
  db_queue.description = queue.description
  db_queue.capacity = queue.capacity
  db_queue.waiting_time = queue.waiting_time

  await db.commit()
  await db.refresh(db_queue)

  return db_queue


async def edit_queue_status(db: AsyncSession, queue: ModifyQueueStatus):
  """Edit queue status by its ID."""
  result = await db.execute(select(QueueTable).filter(QueueTable.id == queue.id))
  db_queue = result.scalars().first()

  if db_queue is None:
    return None

  db_queue.status = queue.status

  await db.commit()
  await db.refresh(db_queue)

  return db_queue


async def edit_queue_active_status(db: AsyncSession, queue: ModifyQueueActiveStatus):
  """Edit queue active status by its ID."""
  result = await db.execute(select(QueueTable).filter(QueueTable.id == queue.id))
  db_queue = result.scalars().first()

  if db_queue is None:
    return None

  db_queue.deactivated = queue.deactivated

  await db.commit()
  await db.refresh(db_queue)

  return db_queue
