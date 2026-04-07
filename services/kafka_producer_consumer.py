import asyncio
import json
import logging
import uuid
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_KAFKA_CONSUMER_COMMON = dict(
    session_timeout_ms=45000,
    heartbeat_interval_ms=15000,
    max_poll_interval_ms=600000,
    request_timeout_ms=120000,
)


class ServiceService:
    def __init__(self, brokers: str, response_topics: list):
        self.brokers = brokers
        self.response_topics = response_topics
        # Must not share group_id with userAndsettings (microservice_request): same group + different
        # subscriptions causes endless rebalances, UnknownMemberIdError, and lost RPC replies.
        self.consumer = AIOKafkaConsumer(
            *self.response_topics,
            bootstrap_servers=self.brokers,
            group_id="catalog_service_group",
            auto_offset_reset="earliest",
            **_KAFKA_CONSUMER_COMMON,
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.brokers,
            request_timeout_ms=120000,
        )
        self.pending_requests = {}

    async def start(self):
        print(f"Starting Kafka Producer and Consumer for topics {self.response_topics}...")
        await self.consumer.start()
        await self.producer.start()

        print("Waiting for Kafka partition assignment...")
        max_wait = 10
        for i in range(max_wait):
            if self.consumer.assignment():
                print(f"Kafka Consumer assigned to: {self.consumer.assignment()}")
                break
            await asyncio.sleep(1)
        else:
            print("Warning: Kafka Consumer started but no partitions assigned yet.")

        asyncio.create_task(self.process_requests())
        print("Kafka Service is now READY.")

    async def process_requests(self):
        print("Listening for Kafka messages...")
        async for msg in self.consumer:
            try:
                request = json.loads(msg.value.decode("utf-8"))
                print(f"DEBUG Kafka: Received message on {msg.topic}: {request}")
                request_id = request.get("request_id")
                if request.get('request_type') == 'service_details':
                    def _load_service():
                        from database import SessionLocal
                        from service import get_service_details

                        s = SessionLocal()
                        try:
                            return get_service_details(s, request["service_id"])
                        finally:
                            s.close()

                    service_data = await asyncio.to_thread(_load_service)
                    response = {"request_id": request_id, "service_id": request["service_id"], "service_data": service_data}
                    await self.producer.send_and_wait("payment_response", json.dumps(response).encode("utf-8"))
                elif request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    future.set_result(request)
            except Exception as e:
                print(f"Error processing Kafka message: {e}")
    
    async def get_cart_data(self, request_topic):
        request_id = str(uuid.uuid4())
        message = json.dumps({"request_id": request_id, "request_type": 'cart_info'}).encode("utf-8")
        
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future

        await self.producer.send_and_wait(request_topic, message)  # Dynamic request topic
        return await future  # Wait for the response
    

    async def stop(self):
        await self.consumer.stop()
        await self.producer.stop()

# Usage
kafka_service_service = ServiceService(brokers="localhost:9092", response_topics=["service_request"])

