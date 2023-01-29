import pika
import redis
from pika import PlainCredentials

# FIXME RabbitMQ connection is being lost
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="rabbitmq",
        port=5672,
        credentials=PlainCredentials("my_user", "my_password"),
    )
)
rabbitmq_client = connection.channel()
rabbitmq_client.queue_declare(queue="summarizer_inference_queue")

redis_client = redis.Redis(host="redis", port=6379)