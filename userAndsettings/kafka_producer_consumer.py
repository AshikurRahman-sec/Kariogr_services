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
    def __init__(self, brokers: str, response_topics: list):
        self.brokers = brokers
        self.consumer = AIOKafkaConsumer(*response_topics, bootstrap_servers=self.brokers, group_id="user_service_group", auto_offset_reset="earliest")
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)
        self.pending_requests = {}

    async def start(self):
        await self.consumer.start()
        await self.producer.start()
        asyncio.create_task(self.process_requests())

    async def process_requests(self):
        async for msg in self.consumer:
            request = json.loads(msg.value.decode("utf-8"))
            request_id = request.get("request_id")
            if request.get('request_type') == 'worker_details':
                db_gen = get_db()
                db = next(db_gen)
                worker_data = await get_worker_details_by_worker_id(request["worker_id"], db)  # Fetch user details
                db_gen.close()
                response = {"request_id": request_id, "worker_id": request["worker_id"], "worker_data": worker_data}
                await self.producer.send_and_wait("payment_response", json.dumps(response).encode("utf-8"))
            if request.get('request_type') == 'user_details':
                db_gen = get_db()
                db = next(db_gen)
                user_data = await get_user_profile_by_user_id(request["user_id"], db)  # Fetch user details
                db_gen.close()
                response = {"request_id": request_id, "user_id": request["user_id"], "user_data": user_data}
                await self.producer.send_and_wait("payment_response", json.dumps(response).encode("utf-8"))
            elif request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                future.set_result(request)  # or request['data']

    async def get_user_auth_info(self, request_topic, user_id: str):
        request_id = str(uuid.uuid4())
        message = json.dumps({"request_id": request_id, "user_id": user_id, "request_type": 'user_auth_info'}).encode("utf-8")
    
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future

        await self.producer.send_and_wait(request_topic, message)  # Dynamic request topic
        return await future  # Wait for the response
    

    async def stop(self):
        await self.consumer.stop()
        await self.producer.stop()

# Usage
kafka_user_settings_service = UserAndSettingsService(brokers="localhost:9092", response_topics=["user_request"])

