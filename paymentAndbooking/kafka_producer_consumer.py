import asyncio
import json
import uuid
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

class PaymentBookingService:
    def __init__(self, brokers: str, response_topics: list):
        self.brokers = brokers
        self.response_topics = response_topics
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)
        self.consumer = AIOKafkaConsumer(*self.response_topics, bootstrap_servers=self.brokers, group_id="payment_group", auto_offset_reset="earliest")
        self.pending_requests = {}

    async def start(self):
        await self.producer.start()
        await self.consumer.start()
        asyncio.create_task(self.listen_for_responses())

    async def listen_for_responses(self):
        async for msg in self.consumer:
            response = json.loads(msg.value.decode("utf-8"))
            request_id = response.get("request_id")
            if request_id in self.pending_requests:
                self.pending_requests[request_id].set_result(response)

    async def get_user_details(self, request_topic, user_id: str):
        request_id = str(uuid.uuid4())
        message = json.dumps({"request_id": request_id, "user_id": user_id, "request_type": 'user_details'}).encode("utf-8")
        
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future

        await self.producer.send_and_wait(request_topic, message)  # Dynamic request topic
        return await future  # Wait for the response
    
    async def get_worker_details(self, request_topic, worker_id: str):
        request_id = str(uuid.uuid4())
        message = json.dumps({"request_id": request_id, "worker_id": worker_id, "request_type": 'worker_details'}).encode("utf-8")
        
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future

        await self.producer.send_and_wait(request_topic, message)  # Dynamic request topic
        return await future  # Wait for the response

    async def stop(self):
        await self.producer.stop()
        await self.consumer.stop()


#Instance Creation
kafka_payment_booking_service = PaymentBookingService(
    brokers="localhost:9092",
    response_topics=["payment_response"]  # Provide response topic
)

