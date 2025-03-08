from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from db.database import get_db
from repository import queue as crud
from schemas import CreateQueue

router = APIRouter()


@router.post("/create")
async def create_queue(queue: CreateQueue, db: AsyncSession = Depends(get_db)):
  """Create a new queue for store"""
  existing_queue = await crud.get_queue_by_store_id_and_queue_type(db, queue)
  if existing_queue:
    raise HTTPException(status_code=400, detail=f"{queue.queue_type} queue already exists for store {queue.store_id}")

  new_queue = await crud.create_queue(db, queue)
  return JSONResponse(
    status_code=201,
    content={
      "message": "Store queue created successfully",
      "storeId": new_queue.store_id,
      "queueType": new_queue.queue_type
    }
  )


@router.get("/get/{store_id}", response_model=list[schemas.QueueResponse])
async def get_queue(store_id: str, db: AsyncSession = Depends(get_db)):
  """Get a list of queues by store id"""
  queue = await crud.get_queues_by_store_id(db, store_id)

  if not queue:
    raise HTTPException(status_code=404, detail="Store queues not found")

  return queue


@router.get("/details/{queue_id}", response_model=schemas.QueueResponse)
async def get_queue_details(queue_id: str, db: AsyncSession = Depends(get_db)):
  """Get a queue details by id"""
  queue = await crud.get_queue_by_id(db, queue_id)

  if not queue:
    raise HTTPException(status_code=404, detail="Queue details not found")

  return queue


@router.post("/edit/details")
async def edit_queue_details(queue: schemas.ModifyQueue, db: AsyncSession = Depends(get_db)):
  updated_queue = await crud.edit_queue_details(db, queue)

  if updated_queue is None:
    raise HTTPException(status_code=404, detail="Queue details not found")

  return JSONResponse(
    status_code=200,
    content={"message": "Queue details updated successfully", "id": updated_queue.id, "storeId": updated_queue.store_id}
  )


@router.post("/edit/status")
async def edit_queue_status(queue: schemas.ModifyQueueStatus, db: AsyncSession = Depends(get_db)):
  updated_queue = await crud.edit_queue_status(db, queue)

  if updated_queue is None:
    raise HTTPException(status_code=404, detail="Queue details not found")

  return JSONResponse(
    status_code=200,
    content={"message": "Queue status updated successfully", "id": updated_queue.id, "storeId": updated_queue.store_id}
  )


@router.post("/edit/active-status")
async def edit_queue_active_status(queue: schemas.ModifyQueueActiveStatus, db: AsyncSession = Depends(get_db)):
  updated_queue = await crud.edit_queue_active_status(db, queue)

  if updated_queue is None:
    raise HTTPException(status_code=404, detail="Queue details not found")

  return JSONResponse(
    status_code=200,
    content={
      "message": f"Queue deactivated status set to {updated_queue.deactivated}",
      "id": updated_queue.id,
      "storeId": updated_queue.store_id
    }
  )
