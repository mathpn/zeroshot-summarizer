"""
Main API endpoints.
"""

import asyncio
import json
import uuid
from typing import Union

import aio_pika
from fastapi import FastAPI, Request

from app.bridge import create_redis_client
from app.logger import logger
from app.models import PendingSummarizationDTO, QueryParams, SummarizationResultDTO

api = FastAPI()


@api.on_event("startup")
async def startup():
    api.state.redis_client = create_redis_client()
    loop = asyncio.get_event_loop()
    api.state.rabbit_conn = await aio_pika.connect(
        host="rabbitmq",
        # host="localhost",
        port=5672,
        login="my_user",
        password="my_password",
        heartbeat=15,
        loop=loop,
    )


@api.post("/classify", status_code=202)
async def classify(request: Request, body: QueryParams) -> PendingSummarizationDTO:
    state = request.app.state
    inference_id = str(uuid.uuid4())

    channel = await state.rabbit_conn.channel()
    queue = await channel.declare_queue(name="summarizer_inference_queue", durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(body.dict()).encode("utf-8"),
            headers={"inference_id": inference_id},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=queue.name,
    )
    logger.info(f"added request to queue (uuid {inference_id})")

    return PendingSummarizationDTO(inference_id=inference_id)


@api.get("/result/{inference_id}")
async def classification_result(
    request: Request, inference_id
) -> Union[SummarizationResultDTO, PendingSummarizationDTO]:
    state = request.app.state
    if not state.redis_client.exists(inference_id):
        return PendingSummarizationDTO(inference_id=inference_id)

    result = state.redis_client.get(inference_id)
    return SummarizationResultDTO(summary=result)
