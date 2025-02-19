import asyncio
import json
import logging
import os
import smtplib
from aiokafka import AIOKafkaConsumer

import email_service as _service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self, brokers: str, group_id: str, topics: list):
        self.brokers = brokers
        self.group_id = group_id
        self.topics = topics
        self.consumer = None
    
    async def start(self):
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.brokers,
            group_id=self.group_id,
            auto_offset_reset="earliest"
        )
        await self.consumer.start()
        logger.info("Kafka Consumer started.")

    async def consume_messages(self):
        if not self.consumer:
            logger.error("Kafka consumer not initialized.")
            return
        
        try:
            async for msg in self.consumer:
                try:
                    data = json.loads(msg.value.decode("utf-8"))
                    if msg.topic == "email_verification":
                        await _service.send_email_verification_otp(data)
                    elif msg.topic == "password_reset":
                        await _service.send_password_reset_email(data)
                except Exception as e:
                    logger.error(f"Failed to process message: {e}")
        except Exception as e:
            logger.critical(f"Consumer crashed: {e}")
        finally:
            await self.consumer.stop()
            logger.info("Kafka Consumer stopped.")

# Kafka Consumer Instance
kafka_consumer_service = KafkaConsumerService(
    brokers="localhost:9092",
    group_id="email_group",
    topics=["email_verification", "password_reset"]
)


# Kafka Consumer Instance
kafka_consumer_service = KafkaConsumerService(
    brokers="localhost:9092",
    group_id="email_notification_group",
    topic="email_notification"
)
