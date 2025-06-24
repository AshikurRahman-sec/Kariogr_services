import asyncio
import json
import logging
import uuid
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from services.user_service import get_user_profile_by_user_id, get_worker_details_by_worker_id
from database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserAndSettingsService:
    def __init__(self, brokers: str):
        self.brokers = brokers
        self.external_consumer = AIOKafkaConsumer(
            "microservice_request",  # topic for requests like 'user_details'
            bootstrap_servers=self.brokers,
            group_id="user_service_group",
            auto_offset_reset="earliest"
        )
        self.internal_consumer = AIOKafkaConsumer(
            "user_request",  # topic for responses like 'user_auth_info'
            bootstrap_servers=self.brokers,
            group_id="user_internal_group",  # different group!
            auto_offset_reset="earliest"
        )
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)
        self.pending_requests = {}

    async def start(self):
        await self.producer.start()
        await self.external_consumer.start()
        await self.internal_consumer.start()

        asyncio.create_task(self.process_external_requests())
        asyncio.create_task(self.process_internal_responses())

    async def process_external_requests(self):
        async for msg in self.external_consumer:
            request = json.loads(msg.value.decode("utf-8"))
            request_id = request.get("request_id")
            if request.get('request_type') == 'user_details':
                db_gen = get_db()
                db = next(db_gen)
                user_data = await get_user_profile_by_user_id(request["user_id"], db)
                db_gen.close()
                response = {
                    "request_id": request_id,
                    "user_id": request["user_id"],
                    "user_data": user_data
                }
                await self.producer.send_and_wait("payment_response", json.dumps(response).encode("utf-8"))

            if request.get('request_type') == 'worker_details':
                db_gen = get_db()
                db = next(db_gen)
                worker_data = await get_worker_details_by_worker_id(request["worker_id"], db)  # Fetch user details
                db_gen.close()
                response = {"request_id": request_id, "worker_id": request["worker_id"], "worker_data": worker_data}
                await self.producer.send_and_wait("payment_response", json.dumps(response).encode("utf-8"))

    async def process_internal_responses(self):
        async for msg in self.internal_consumer:
            request = json.loads(msg.value.decode("utf-8"))
            request_id = request.get("request_id")
            if request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                future.set_result(request)

    async def get_user_auth_info(self, request_topic, user_id: str):
        request_id = str(uuid.uuid4())
        message = json.dumps({"request_id": request_id, "user_id": user_id, "request_type": 'user_auth_info'}).encode("utf-8")
    
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future

        await self.producer.send_and_wait(request_topic, message)  # Dynamic request topic
        return await future  # Wait for the response
    

    async def stop(self):
        await self.external_consumer.stop()
        await self.internal_consumer.stop()
        await self.producer.stop()

# Usage
kafka_user_settings_service = UserAndSettingsService(brokers="localhost:9092")

