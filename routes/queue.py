from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from repository import queue as crud
from schemas import CreateQueue

router = APIRouter()


@router.post("/create")
async def create_queue(queue: CreateQueue, db: AsyncSession = Depends(get_db)):
  """Create a new queue for store"""
  existing_queue = await crud.get_queue_by_store_id_and_queue_type(db, queue)
  if existing_queue:
    raise HTTPException(status_code=400,
                        detail=f"{queue.queue_type} queue already exists for store {queue.store_id}")

  new_queue = await crud.create_queue(db, queue)
  return JSONResponse(
    status_code=201,
    content={
      "message": "Store queue created successfully",
      "storeId": new_queue.store_id,
      "queueType": new_queue.queue_type
    }
  )
