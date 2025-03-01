import asyncio
import uvicorn

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aws.sqs import poll_sqs
from db.database import init_db

# from routes import queue

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Startup and shutdown event handler"""

  # Initialize the database at startup
  await init_db()

  # Start polling SQS for new messages
  task_poll_sqs = asyncio.create_task(poll_sqs())

  yield
  task_poll_sqs.cancel()


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

if __name__ == "__main__":
  uvicorn.run("app:app", host="0.0.0.0", port=5000)
