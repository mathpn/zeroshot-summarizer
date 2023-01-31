"""
Pydantic data models.
"""

import uuid
from typing import Optional

from pydantic import BaseModel


class PendingSummarizationDTO(BaseModel):
    inference_id: str


class SummarizationResultDTO(BaseModel):
    summary: str


class QueryParams(BaseModel):
    sequence: str
    descriptors: list[str]
    max_length: int = 20
    temperature: float = 0.1
    def __post_init__(self):
        self.inference_id = str(uuid.uuid4())
