import asyncio
import json
import uuid
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from database import get_db
from service import get_cart_data

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
        asyncio.create_task(self.process_requests())

    async def process_requests(self):
        async for msg in self.consumer:
            request = json.loads(msg.value.decode("utf-8"))
            request_id = request.get("request_id")
            if request.get('request_type') == 'cart_info':
                db_gen = get_db()
                db = next(db_gen)
                cart_data = get_cart_data(db)  # Fetch user details
                #print(cart_data)
                db_gen.close()
                response = {"request_id": request_id, "cart_data": cart_data}
                await self.producer.send_and_wait("service_request", json.dumps(response).encode("utf-8"))
            elif request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                future.set_result(request)  # or request['data']

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
    
    async def get_service_details(self, request_topic, service_id: str):
        request_id = str(uuid.uuid4())
        message = json.dumps({"request_id": request_id, "service_id": service_id, "request_type": 'service_details'}).encode("utf-8")
        
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

