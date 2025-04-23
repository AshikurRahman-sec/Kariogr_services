import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from database import get_db
from service import get_service_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceService:
    def __init__(self, brokers: str, response_topics: list):
        self.brokers = brokers
        self.consumer = AIOKafkaConsumer(*response_topics, bootstrap_servers=self.brokers, group_id="user_service_group", auto_offset_reset="earliest")
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)

    async def start(self):
        await self.consumer.start()
        await self.producer.start()
        asyncio.create_task(self.process_requests())

    async def process_requests(self):
        async for msg in self.consumer:
            request = json.loads(msg.value.decode("utf-8"))
            request_id = request.get("request_id")
            if request.get('request_type') == 'service_details':
                db_gen = get_db()
                db = next(db_gen)
                service_data = get_service_details(db, request["service_id"])  # Fetch user details
                db_gen.close()
                response = {"request_id": request_id, "service_id": request["service_id"], "service_data": service_data}
                await self.producer.send_and_wait("payment_response", json.dumps(response).encode("utf-8"))
            
    

    async def stop(self):
        await self.consumer.stop()
        await self.producer.stop()

# Usage
kafka_service_service = ServiceService(brokers="localhost:9092", response_topics=["service_request"])

