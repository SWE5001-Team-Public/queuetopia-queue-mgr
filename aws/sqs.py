import asyncio
import json
import logging
import os

import boto3

from config import load_environment, setup_logging
from db.database import get_db
from repository.store import create_store, edit_store, edit_store_status
from schemas import CreateStore, EditStore, EditStoreStatus

load_environment()
setup_logging()

logger = logging.getLogger(__name__)

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

# AWS SQS Configuration
AWS_REGION = os.getenv("AWS_REGION")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL")
AWS_SQS_DLQ_URL = os.getenv("AWS_SQS_DLQ_URL")
MAX_RETRIES = 3

# Create SQS client
sqs_client = boto3.client(
  "sqs",
  region_name=AWS_REGION,
  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


async def poll_sqs():
  """Continuously poll SQS for new messages"""
  while True:
    logger.info(f"🔎 Polling SQS for new messages")

    response = sqs_client.receive_message(
      QueueUrl=AWS_SQS_QUEUE_URL,
      MaxNumberOfMessages=1,
      WaitTimeSeconds=1,
      AttributeNames=["All"]
    )

    messages = response.get("Messages", [])
    for message in messages:
      receipt_handle = message["ReceiptHandle"]
      body = message["Body"]
      message_group_id = message.get("Attributes", {}).get("MessageGroupId", None)

      try:
        result = await process_message(body, message_group_id)

        if result is True:
          sqs_client.delete_message(QueueUrl=AWS_SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
          logger.info("✅ Message processed and deleted")
        else:
          logger.warning(f"⚠️ Processing failed")
          sqs_client.change_message_visibility(
            QueueUrl=AWS_SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=0
          )
          logger.info("🔄 Message visibility timeout reset")

      except Exception as e:
        logger.error(f"⚠️ Processing failed with exception: {str(e)}")
        sqs_client.change_message_visibility(
          QueueUrl=AWS_SQS_QUEUE_URL,
          ReceiptHandle=receipt_handle,
          VisibilityTimeout=0
        )
        logger.info("🔄 Message visibility timeout reset")

    await asyncio.sleep(1)


async def process_message(body, message_group_id):
  """Process message body and save to database"""
  logger.info(f"⌛ Processing {message_group_id} event message: {body}")

  if message_group_id == 'store-create-event':
    try:
      converted_obj = json.loads(body)
      logger.info(f"{converted_obj}")
      new_store = CreateStore(
        id=converted_obj["id"],
        s_id=converted_obj["s_id"],
        name=converted_obj["name"],
        alias=converted_obj["alias"],
        company_id=converted_obj["company_id"]
      )

      async for db in get_db():
        await create_store(db, new_store)
        logger.info("✅ Store created successfully")
        return True
    except Exception as e:
      logger.error(f"⚠️ Store creation failed with exception: {str(e)}")
      return False

  if message_group_id == 'store-update-event':
    try:
      converted_obj = json.loads(body)
      modified_store = EditStore(
        id=converted_obj["id"],
        name=converted_obj["name"],
        alias=converted_obj["alias"]
      )

      async for db in get_db():
        await edit_store(db, modified_store)
        logger.info("✅ Store updated successfully")
        return True
    except Exception as e:
      logger.error(f"⚠️ Store update failed with exception: {str(e)}")
      return False

  if message_group_id == 'store-deactivate-event':
    try:
      converted_obj = json.loads(body)
      logger.info(f"{converted_obj}")
      modified_store = EditStoreStatus(
        id=converted_obj["id"],
        deactivated=True,
      )

      async for db in get_db():
        await edit_store_status(db, modified_store)
        logger.info("✅ Store deactivated successfully")
        return True
    except Exception as e:
      logger.error(f"⚠️ Store deactivation failed with exception: {str(e)}")
      return False

  return False
