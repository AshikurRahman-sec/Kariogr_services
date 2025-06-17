import asyncio
import json
import uuid
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from database import get_db
from services.auth_service import get_user

class PaymentBookingService:
    def __init__(self, brokers: str, response_topics: list):
        self.brokers = brokers
        self.response_topics = response_topics
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)
        self.consumer = AIOKafkaConsumer(*self.response_topics, bootstrap_servers=self.brokers, group_id="auth_group", auto_offset_reset="earliest")
        self.pending_requests = {}

    async def start(self):
        await self.producer.start()
        await self.consumer.start()
        asyncio.create_task(self.process_requests())

    async def process_requests(self):
        async for msg in self.consumer:
            request = json.loads(msg.value.decode("utf-8"))
            request_id = request.get("request_id")
            if request.get('request_type') == 'user_auth_info':
                user_id = request.get("user_id")
                db_gen = get_db()
                db = next(db_gen)
                user_data = get_user(db, user_id)  # Fetch user details
                #print(cart_data)
                db_gen.close()
                response = {"request_id": request_id, "user_data": user_data}
                await self.producer.send_and_wait("user_request", json.dumps(response).encode("utf-8"))
            elif request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                future.set_result(request)  # or request['data']

    async def send_message(self, topic: str, value: dict):
        if not self.producer:
            raise Exception("Producer not started.")
        
        message = json.dumps(value).encode("utf-8")
        await self.producer.send_and_wait(topic, message)
    
    async def stop(self):
        await self.producer.stop()
        await self.consumer.stop()


#Instance Creation
kafka_auth_service = PaymentBookingService(
    brokers="localhost:9092",
    response_topics=["auth_info"]  # Provide response topic
)

