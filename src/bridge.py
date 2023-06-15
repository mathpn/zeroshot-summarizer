"""
RabbitMQ connection utils.
"""

import aio_pika
import pika
from pika import PlainCredentials


def create_rabbitmq_client():
    rabbit_conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            # host="localhost",
            port=5672,
            credentials=PlainCredentials("my_user", "my_password"),
            heartbeat=15,
        )
    )
    channel = rabbit_conn.channel()
    return channel, rabbit_conn


async def async_connect_rabbitmq(loop):
    rabbit_conn = await aio_pika.connect(
        host="rabbitmq",
        # host="localhost",
        port=5672,
        login="my_user",
        password="my_password",
        heartbeat=15,
        loop=loop,
    )
    return rabbit_conn
