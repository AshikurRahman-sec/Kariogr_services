import asyncio
import json
import uuid
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from services.auth_service import get_user

_KAFKA_CONSUMER_COMMON = dict(
    session_timeout_ms=45000,
    heartbeat_interval_ms=15000,
    max_poll_interval_ms=600000,
    request_timeout_ms=120000,
)


class AuthService:
    def __init__(self, brokers: str, response_topics: list):
        self.brokers = brokers
        self.response_topics = response_topics
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.brokers,
            request_timeout_ms=120000,
        )
        self.consumer = AIOKafkaConsumer(
            *self.response_topics,
            bootstrap_servers=self.brokers,
            group_id="auth_group",
            auto_offset_reset="earliest",
            **_KAFKA_CONSUMER_COMMON,
        )
        self.pending_requests = {}

    async def start(self):
        print(f"Starting Kafka Producer and Consumer for topics {self.response_topics}...")
        await self.producer.start()
        await self.consumer.start()
        
        print("Waiting for Kafka partition assignment...")
        max_wait = 10
        for i in range(max_wait):
            if self.consumer.assignment():
                print(f"Kafka Consumer assigned to: {self.consumer.assignment()}")
                break
            await asyncio.sleep(1)
        else:
            print("Warning: Kafka Consumer started without partitions assigned yet.")

        asyncio.create_task(self.process_requests())
        print("Kafka Service is now READY.")

    async def process_requests(self):
        from services.auth_service import get_user
        print("Listening for Kafka messages...")
        async for msg in self.consumer:
            try:
                request = json.loads(msg.value.decode("utf-8"))
                print(f"DEBUG Kafka: Received message on {msg.topic}: {request}")
                request_id = request.get("request_id")
                if request.get('request_type') == 'user_auth_info':
                    user_id = request.get("user_id")
                    user_data = await get_user(None, user_id)
                    response = {"request_id": request_id, "user_data": user_data}
                    await self.producer.send_and_wait("user_request", json.dumps(response).encode("utf-8"))
                elif request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    future.set_result(request)
            except Exception as e:
                print(f"Error processing Kafka message: {e}")

    async def send_message(self, topic: str, value: dict):
        if not self.producer:
            raise Exception("Producer not started.")
        
        message = json.dumps(value).encode("utf-8")
        await self.producer.send_and_wait(topic, message)
    
    async def stop(self):
        await self.producer.stop()
        await self.consumer.stop()


#Instance Creation
kafka_auth_service = AuthService(
    brokers="localhost:9092",
    response_topics=["auth_info"]  # Provide response topic
)

