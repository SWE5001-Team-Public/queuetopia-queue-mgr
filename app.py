import asyncio
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aws.sqs import poll_sqs
from db.database import init_db, insert_static
from routes import config

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Startup and shutdown event handler"""

  # Initialize the database at startup
  await init_db()
  await insert_static()

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


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
  """Health check endpoint for monitoring service status."""
  return {"status": "healthy"}


# Other routes
app.include_router(config.router, prefix="/config", tags=["Static Configurations"])

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=5000)
