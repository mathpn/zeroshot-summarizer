"""
Main API endpoints.
"""

import asyncio
import json
import uuid
from functools import partial

import aio_pika
from fastapi import FastAPI, Request

from app.models import QueryParams, SummarizationResultDTO
from app.producer import AIOProducer
from app.utils import timed
from src.bridge import async_connect_rabbitmq
from src.logger import logger

app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    loop = asyncio.get_event_loop()
    conn = await async_connect_rabbitmq(loop)
    app.state.rabbit_conn = conn
    app.state.channel = await conn.channel()
    await app.state.channel.set_qos(prefetch_count=1)
    app.state.producer = AIOProducer({"bootstrap.servers": "broker:9092"}, loop=loop)


@app.on_event("shutdown")
async def shutdown() -> None:
    app.state.producer.close()


@app.get("/health")
async def health():
    return "OK"


async def result_callback(message: aio_pika.abc.AbstractIncomingMessage, queue, inference_id: str):
    if message.headers["inference_id"] != inference_id:
        logger.warning(
            "message with different ID on exclusive queue: uuid = %s",
            message.headers["inference_id"],
        )
        return

    logger.debug("received result - uuid = %s", inference_id)
    await queue.put(message)
    await message.ack()


@app.post("/summarize", status_code=200)
@timed
async def classify(request: Request, body: QueryParams) -> SummarizationResultDTO:
    state = request.app.state
    inference_id = str(uuid.uuid4())

    out_queue = asyncio.Queue()
    channel = state.channel
    result = await channel.declare_queue(name=inference_id, exclusive=True, auto_delete=True)
    body = json.dumps(body.dict())
    res = await state.producer.produce("inference_queue", body, inference_id)
    # TODO handle res
    logger.info("added request to queue (uuid %s)", inference_id)

    callback = partial(result_callback, queue=out_queue, inference_id=inference_id)
    task = asyncio.create_task(result.consume(callback))
    out = await out_queue.get()
    task.cancel()
    logger.info("received result (uuid %s)", inference_id)

    return SummarizationResultDTO(summary=out.body.decode("utf-8"))
