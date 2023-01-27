"""
Main API endpoints.
"""

import json
import uuid
from typing import Union

from fastapi import FastAPI
from pika import BasicProperties
from pydantic import BaseModel

from app.bridge import rabbitmq_client, redis_client

api = FastAPI()


class PendingSummarizationDTO(BaseModel):
    inference_id: str


class SummarizationResultDTO(BaseModel):
    summary: str


class QueryParams(BaseModel):
    sequence: str
    descriptors: list[str]
    max_length: int = 20
    temperature: float = 0.1


@api.post("/classify", status_code=202)
async def classify(body: QueryParams) -> PendingSummarizationDTO:
    inference_id = str(uuid.uuid4())

    rabbitmq_client.basic_publish(
        exchange="",  # default exchange
        routing_key="summarizer_inference_queue",
        body=json.dumps(body.dict()),
        properties=BasicProperties(headers={"inference_id": inference_id}),
    )

    return PendingSummarizationDTO(inference_id=inference_id)


@api.get("/result/{inference_id}")
async def classification_result(
    inference_id,
) -> Union[SummarizationResultDTO, PendingSummarizationDTO]:
    if not redis_client.exists(inference_id):
        return PendingSummarizationDTO(inference_id=inference_id)

    result = redis_client.get(inference_id)
    return SummarizationResultDTO(summary=result)
