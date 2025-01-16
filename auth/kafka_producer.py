from aiokafka import AIOKafkaProducer
import asyncio
import json

class KafkaProducerService:
    def __init__(self, brokers: str):
        self.brokers = brokers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)
        await self.producer.start()

    async def send_message(self, topic: str, value: dict):
        if not self.producer:
            raise Exception("Producer not started.")
        
        message = json.dumps(value).encode("utf-8")
        await self.producer.send_and_wait(topic, message)

    async def stop(self):
        if self.producer:
            await self.producer.stop()

# Kafka producer instance
kafka_producer_service = KafkaProducerService(brokers="localhost:9092")
