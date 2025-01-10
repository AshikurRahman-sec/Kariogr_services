import asyncio
import email_service
from dotenv import load_dotenv
from fastapi import FastAPI
from app.kafka_consumer import kafka_consumer_service

# Load environment variables
load_dotenv()

app = FastAPI()    

@app.on_event("startup")
async def startup_event():
    await kafka_consumer_service.start()
    asyncio.create_task(kafka_consumer_service.consume_messages())