from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import StaticTable


async def get_queue_types(db: AsyncSession):
  """Get all queue types from static table."""
  result = await db.execute(select(StaticTable).filter(StaticTable.type == "Queue"))
  return result.scalars().all()
