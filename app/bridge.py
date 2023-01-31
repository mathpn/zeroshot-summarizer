"""
Connection utils.
"""

import pika
import redis
from pika import PlainCredentials

# FIXME RabbitMQ connection is being lost in FastAPI
def create_rabbitmq_client():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            # host="localhost",
            port=5672,
            credentials=PlainCredentials("my_user", "my_password"),
            heartbeat=15,
        )
    )
    rabbitmq_client = connection.channel()
    rabbitmq_client.queue_declare(queue="summarizer_inference_queue", durable=True)
    return rabbitmq_client, connection


def create_redis_client():
    return redis.Redis(host="redis", port=6379)
    # return redis.Redis(host="localhost", port=6379)
