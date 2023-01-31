"""
Main API endpoints.
"""

import asyncio
import json
import uuid
from typing import Union

import pika
from fastapi import FastAPI, Request

from app.bridge import create_rabbitmq_client, create_redis_client
from app.logger import logger
from app.models import (PendingSummarizationDTO, QueryParams,
                        SummarizationResultDTO)
from app.publisher import RabbitPublisher

api = FastAPI()


@api.on_event("startup")
def startup():
    # api.state.rabbitmq_client = create_rabbitmq_client()
    api.state.redis_client = create_redis_client()
    api.state.publisher = RabbitPublisher(create_rabbitmq_client)
    asyncio.create_task(api.state.publisher.run())


@api.post("/classify", status_code=202)
async def classify(request: Request, body: QueryParams) -> PendingSummarizationDTO:
    state = request.app.state
    inference_id = str(uuid.uuid4())

    # with create_rabbitmq_client() as rabbitmq_client:
    #     rabbitmq_client.basic_publish(
    #         exchange="",  # default exchange
    #         routing_key="summarizer_inference_queue",
    #         body=json.dumps(body.dict()),
    #         properties=pika.BasicProperties(
    #             headers={"inference_id": inference_id}, delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    #         ),
    #     )
    await state.publisher.add(body, inference_id)
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
