"""
Main API endpoints.
"""

import asyncio
import json
import uuid
from functools import partial

import aio_pika
from fastapi import FastAPI, Request

from src.bridge import async_connect_rabbitmq
from src.logger import logger
from app.models import QueryParams, SummarizationResultDTO
from app.utils import timed

api = FastAPI()


@api.on_event("startup")
async def startup() -> None:
    loop = asyncio.get_event_loop()
    conn = await async_connect_rabbitmq(loop)
    api.state.rabbit_conn = conn


async def result_callback(message: aio_pika.abc.AbstractIncomingMessage, queue, inference_id: str):
    if message.headers["inference_id"] != inference_id:
        logger.warning(
            f"message with different ID on exclusive queue: uuid = {message.headers['inference_id']}"
        )
        return

    logger.debug(f"received result - uuid = {inference_id}")
    await queue.put(message)
    await message.ack()


@api.post("/summarize", status_code=200)
@timed
async def classify(request: Request, body: QueryParams) -> SummarizationResultDTO:
    state = request.app.state
    inference_id = str(uuid.uuid4())

    out_queue = asyncio.Queue()
    channel = await state.rabbit_conn.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(name="summarizer_inference_queue", durable=True)
    result = await channel.declare_queue(name=inference_id, exclusive=True, auto_delete=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(body.dict()).encode("utf-8"),
            headers={"inference_id": inference_id},
            reply_to=result.name,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=queue.name,
    )
    logger.info(f"added request to queue (uuid {inference_id})")

    callback = partial(result_callback, queue=out_queue, inference_id=inference_id)
    task = asyncio.create_task(result.consume(callback))
    out = await out_queue.get()
    task.cancel()
    await channel.close()
    logger.info(f"received result (uuid {inference_id})")

    return SummarizationResultDTO(summary=out.body.decode("utf-8"))
