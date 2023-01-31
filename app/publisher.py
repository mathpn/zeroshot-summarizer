"""
RabbitMQ publisher.
"""

import asyncio
import json
from typing import Callable

import pika

from app.models import QueryParams


# FIXME this solution is pretty crappy. Find a way to keep channel connection open (heartbeat).
class RabbitPublisher:
    def __init__(self, rabbitmq_creator: Callable):
        self.channel, self.rabbit_conn = rabbitmq_creator()
        self.queue = asyncio.Queue()

    async def run(self):
        while True:
            try:
                item: QueryParams = self.queue.get_nowait()
                inference_id = item.pop("inference_id")
                self.channel.basic_publish(
                    exchange="",  # default exchange
                    routing_key="summarizer_inference_queue",
                    body=json.dumps(item),
                    properties=pika.BasicProperties(
                        headers={"inference_id": inference_id},
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                    ),
                )
            except asyncio.QueueEmpty:
                self.rabbit_conn.process_data_events()
                await asyncio.sleep(0.1)

    async def add(self, body: QueryParams, inference_id: str):
        await self.queue.put({**body.dict(), "inference_id": inference_id})
