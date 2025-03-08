from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from db.database import get_db
from repository import static as crud

router = APIRouter()


@router.get("/queue-types", response_model=list[schemas.QueueTypeResponse])
async def get_queue_types(db: AsyncSession = Depends(get_db)):
  """Retrieve a list of queue types"""
  user = await crud.get_queue_types(db)

  if not user:
    raise HTTPException(status_code=404, detail="Static queue types not found")

  return user
