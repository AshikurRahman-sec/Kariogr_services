import asyncio
import json
import logging
import os
import smtplib
from aiokafka import AIOKafkaConsumer


from email_service import notification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self, brokers: str, group_id: str, topic: str):
        self.brokers = brokers
        self.group_id = group_id
        self.topic = topic
        self.consumer = None  # Initialize in `start()`
    
    async def start(self):
        """
        Initializes and starts the Kafka consumer.
        """
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.brokers,
            group_id=self.group_id,
            auto_offset_reset="earliest"
        )
        await self.consumer.start()
        logger.info("Kafka Consumer started.")

    async def consume_messages(self):
        """
        Continuously consumes messages and processes them.
        """
        if not self.consumer:
            logger.error("Kafka consumer not initialized.")
            return

        try:
            async for msg in self.consumer:
                try:
                    data = json.loads(msg.value.decode("utf-8"))
                    await notification(data)
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
    group_id="email_notification_group",
    topic="email_notification"
)
