from aiokafka import AIOKafkaConsumer
from email_service import notification
import asyncio
import json

class KafkaConsumerService:
    def __init__(self, brokers: str, group_id: str, topic: str):
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=brokers,
            group_id=group_id,
            auto_offset_reset="earliest"
        )

    async def start(self):
        await self.consumer.start()

    async def consume_messages(self):
        try:
            async for msg in self.consumer:
                data = json.loads(msg.value.decode("utf-8"))
                await self.notification(data)
        finally:
            await self.consumer.stop()


# Kafka consumer instance
kafka_consumer_service = KafkaConsumerService(
    brokers="localhost:9092",
    group_id="email_notification_group",
    topic="email_notification"
)
