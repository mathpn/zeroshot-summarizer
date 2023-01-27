"""
Inference worker that uses RabbitMQ (pika) and stores result on a Redis instance.
"""

import json

import torch
from pika import BasicProperties
from transformers import T5ForConditionalGeneration, T5Tokenizer

from app.bridge import rabbitmq_client, redis_client
from app.model import create_inference


def callback(channel, method, properties: BasicProperties, body: str) -> None:
    kwargs = json.loads(body)
    result = inference(**kwargs)
    print(f"Result: {result}")

    redis_client.set(properties.headers["inference_id"], result, ex=60)
    channel.basic_ack(delivery_tag=method.delivery_tag)


tokenizer = T5Tokenizer.from_pretrained("t5-small", model_max_length=512)
model = T5ForConditionalGeneration.from_pretrained("t5-small")
model.load_state_dict(torch.load("./t5_small_ft_22.pth", map_location="cpu"))

inference = create_inference(model, tokenizer)

rabbitmq_client.basic_qos(prefetch_count=1)
rabbitmq_client.basic_consume(queue="summarizer_inference_queue", on_message_callback=callback)
rabbitmq_client.start_consuming()
