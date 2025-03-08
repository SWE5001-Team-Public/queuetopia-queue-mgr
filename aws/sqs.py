import asyncio
import json
import os

import boto3
from dotenv import load_dotenv

from db.database import get_db
from repository.store import create_store, edit_store, edit_store_status
from schemas import CreateStore, EditStore, EditStoreStatus

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

if ENVIRONMENT == "prod":
  load_dotenv(".env.production")
elif ENVIRONMENT == "local":
  load_dotenv(".env.local")
else:
  load_dotenv(".env")

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
    print(f"🔎 Polling queue for new messages")

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
          print("✅ Message processed and deleted")
        else:
          print(f"⚠️ Processing failed")
          sqs_client.change_message_visibility(
            QueueUrl=AWS_SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=0
          )
          print("🔄 Message visibility timeout reset")

      except Exception as e:
        print(f"⚠️ Processing failed with exception: {str(e)}")
        sqs_client.change_message_visibility(
          QueueUrl=AWS_SQS_QUEUE_URL,
          ReceiptHandle=receipt_handle,
          VisibilityTimeout=0
        )
        print("🔄 Message visibility timeout reset")

    await asyncio.sleep(1)


async def process_message(body, message_group_id):
  """Process message body and save to database"""
  print(f"⌛ Processing {message_group_id} event message: {body}")

  if message_group_id == 'store-create-event':
    try:
      converted_obj = json.loads(body)
      print(f"{converted_obj}")
      new_store = CreateStore(
        id=converted_obj["id"],
        s_id=converted_obj["s_id"],
        name=converted_obj["name"],
        alias=converted_obj["alias"],
        company_id=converted_obj["company_id"]
      )

      async for db in get_db():
        await create_store(db, new_store)
        print("✅ Store created successfully")
        return True
    except Exception as e:
      print(f"⚠️ Store creation failed with exception: {str(e)}")
      return False

  if message_group_id == 'store-update-event':
    try:
      converted_obj = json.loads(body)
      print(f"{converted_obj}")
      modified_store = EditStore(
        id=converted_obj["id"],
        name=converted_obj["name"],
        alias=converted_obj["alias"]
      )

      async for db in get_db():
        await edit_store(db, modified_store)
        print("✅ Store updated successfully")
        return True
    except Exception as e:
      print(f"⚠️ Store update failed with exception: {str(e)}")
      return False

  if message_group_id == 'store-deactivate-event':
    try:
      converted_obj = json.loads(body)
      print(f"{converted_obj}")
      modified_store = EditStoreStatus(
        id=converted_obj["id"],
        deactivated=True,
      )

      async for db in get_db():
        await edit_store_status(db, modified_store)
        print("✅ Store deactivated successfully")
        return True
    except Exception as e:
      print(f"⚠️ Store deactivation failed with exception: {str(e)}")
      return False

  return False
