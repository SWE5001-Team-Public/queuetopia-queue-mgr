import logging
import os
import ssl

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import load_environment, setup_logging
from db.base import Base
from db.models import StaticTable, StoreTable, QueueTable

load_environment()
setup_logging()

logger = logging.getLogger(__name__)

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
DATABASE_URL = os.getenv("DATABASE_URL")

logger.info(f"🚀 Running in {ENVIRONMENT.upper()} environment")

# Ensure DATABASE_URL is set
if not DATABASE_URL:
  raise ValueError("DATABASE_URL is not set. Check your .env file.")

# Configure SSL context for production database (only if needed)
ssl_context = ssl.create_default_context() if ENVIRONMENT == "prod" else None

# Create async engine
engine = create_async_engine(
  DATABASE_URL,
  echo=True,
  pool_pre_ping=True,
  connect_args={"ssl": ssl_context} if ssl_context else {}
)

SessionLocal = sessionmaker(
  autocommit=False,
  autoflush=False,
  class_=AsyncSession,
  expire_on_commit=False
)


# Function to create tables asynchronously
async def create_tables():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


# Run table creation when the application starts
async def init_db():
  await create_tables()


# Insert static values
async def insert_static():
  async with SessionLocal(bind=engine) as session:
    try:
      records = [
        StaticTable(key='Open', value='Open', type='Queue_Status'),
        StaticTable(key='Closed', value='Closed', type='Queue_Status'),
        StaticTable(key='Virtual', value='Virtual', type='Queue_Type'),
        StaticTable(key='Physical', value='Physical', type='Queue_Type'),
      ]
      session.add_all(records)
      await session.commit()
    except Exception as e:
      await session.rollback()
      logger.error(f"Error inserting records: {e}")


# Insert test data
async def insert_test_data():
  stores = [
    # Stores for Coffee Paradise
    StoreTable(
      id='eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
      s_id=1,
      name='Downtown Café',
      alias='CP',
      deactivated=False,
      company_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    ),
    StoreTable(
      id='ffffffff-ffff-ffff-ffff-ffffffffffff',
      s_id=2,
      name='Riverside Coffee',
      alias='CP',
      deactivated=False,
      company_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    ),
    # Stores for Sushi Bar
    StoreTable(
      id='11111111-gggg-gggg-gggg-gggggggggggg',
      s_id=3,
      name='Ueno',
      alias='SB',
      deactivated=False,
      company_id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    ),
    StoreTable(
      id='22222222-hhhh-hhhh-hhhh-hhhhhhhhhhhh',
      s_id=4,
      name='Nagoya',
      alias='SB',
      deactivated=False,
      company_id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
    ),
    # Stores for WOW KBBQ
    StoreTable(
      id='33333333-iiii-iiii-iiii-iiiiiiiiiiii',
      s_id=5,
      name='Yishun',
      alias='WK',
      deactivated=False,
      company_id='cccccccc-cccc-cccc-cccc-cccccccccccc'
    ),
    StoreTable(
      id='44444444-jjjj-jjjj-jjjj-jjjjjjjjjjjj',
      s_id=6,
      name='Bedok',
      alias='WK',
      deactivated=False,
      company_id='cccccccc-cccc-cccc-cccc-cccccccccccc'
    ),
    # Stores for Gourmet Dining
    StoreTable(
      id='55555555-kkkk-kkkk-kkkk-kkkkkkkkkkkk',
      s_id=7,
      name='Seaside Bistro',
      alias='GD',
      deactivated=False,
      company_id='dddddddd-dddd-dddd-dddd-dddddddddddd'
    ),
    StoreTable(
      id='66666666-llll-llll-llll-llllllllllll',
      s_id=8,
      name='Mountain View Restaurant',
      alias='GD',
      deactivated=False,
      company_id='dddddddd-dddd-dddd-dddd-dddddddddddd'
    )
  ]

  # Step 0: Clean existing data first
  async with SessionLocal(bind=engine) as session:
    try:
      # Delete in reverse order to respect foreign key constraints
      await session.execute(delete(QueueTable))
      await session.execute(delete(StoreTable))

      # Reset sequences if they exist
      await session.execute("ALTER SEQUENCE IF EXISTS queue_q_id_seq RESTART WITH 1")
      await session.execute("ALTER SEQUENCE IF EXISTS store_s_id_seq RESTART WITH 1")

      await session.commit()
      logger.info("Cleaned existing test data and reset sequences")
    except Exception as e:
      await session.rollback()
      logger.error(f"Error cleaning existing data: {e}")

  # Step 1: Insert stores
  async with SessionLocal(bind=engine) as session:
    try:
      session.add_all(stores)
      await session.commit()
      logger.info("Successfully inserted test stores")
    except Exception as e:
      await session.rollback()
      logger.error(f"Error inserting test stores: {e}")

  # Step 2: Create Virtual queue for each store
  async with SessionLocal(bind=engine) as session:
    try:
      # Create a Virtual queue for each store
      queues = []
      queue_counter = 1

      for store in stores:
        queues.append(
          QueueTable(
            id=f"q{queue_counter:07d}-0000-0000-0000-000000000000",
            queue_type="Virtual",
            description=f"Virtual queue for {store.name}",
            status="Open",
            capacity=0,
            deactivated=False,
            store_id=store.id
          )
        )
        queue_counter += 1

      session.add_all(queues)
      await session.commit()
      logger.info("Successfully created Virtual queues for all stores")
    except Exception as e:
      await session.rollback()
      logger.error(f"Error creating queues: {e}")

  logger.info("Test data insertion complete")


# Dependency for async DB session
async def get_db():
  async with SessionLocal(bind=engine) as session:
    yield session
