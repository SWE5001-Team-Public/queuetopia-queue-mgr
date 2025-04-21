import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from aws.sqs import poll_sqs
from config import load_environment
from db.database import init_db, insert_static, insert_test_data
from routes import config, queue

load_environment()

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Startup and shutdown event handler"""

  # Initialize the database at startup
  await init_db()
  await insert_static()

  if ENVIRONMENT == "local":
    await insert_test_data()

  # Start polling SQS for new messages asynchronously
  task_poll_sqs = asyncio.create_task(poll_sqs())

  yield

  # Clean up the background SQS polling when shutting down
  task_poll_sqs.cancel()
  try:
    await task_poll_sqs
  except asyncio.CancelledError:
    pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

router = APIRouter(prefix="/queue-mgr")


# Health check endpoint
@router.get("/health", tags=["System"])
async def health_check():
  """Health check endpoint for monitoring service status."""
  return {"status": "healthy"}


# Other routes
router.include_router(config.router, prefix="/config", tags=["Static Configurations"])
router.include_router(queue.router, prefix="/queue", tags=["Queue"])

app.include_router(router)

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=5000)
