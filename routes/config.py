from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from db.database import get_db
from repository import static as crud

router = APIRouter()


@router.get("/queue-status", response_model=list[schemas.ConfigResponse])
async def get_queue_status(db: AsyncSession = Depends(get_db)):
  """Retrieve a list of queue statuses"""
  queue_status = await crud.get_queue_status(db)

  if not queue_status:
    raise HTTPException(status_code=404, detail="Static queue statuses not found")

  return queue_status


@router.get("/queue-types", response_model=list[schemas.ConfigResponse])
async def get_queue_types(db: AsyncSession = Depends(get_db)):
  """Retrieve a list of queue types"""
  queue_types = await crud.get_queue_types(db)

  if not queue_types:
    raise HTTPException(status_code=404, detail="Static queue types not found")

  return queue_types
