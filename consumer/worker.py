
import argparse
import asyncio
import json
import queue
import sys
import threading
import time
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from functools import partial
from threading import Thread
from typing import Any, Callable

import torch
from confluent_kafka import OFFSET_BEGINNING, Consumer
from pika import BasicProperties
from transformers import T5ForConditionalGeneration, T5Tokenizer

from consumer.model import InferenceResult, build_query, create_inference
from src.bridge import create_rabbitmq_client
from src.logger import logger


class InferenceConsumer(Thread):
    def __init__(
        self,
        worker_id: int,
        config: dict[str, Any],
        topic: str,
        inference_fn: Callable,
        max_batch_size: int = 32,
        wait_time: float = 0.1,
    ):
        super().__init__()
        self.is_running = True
        self.worker_id = worker_id
        self.consumer = Consumer(config)
        self.consumer.subscribe([topic])
        self.max_size = max_batch_size
        self.wait_time = wait_time
        self.inference_fn = inference_fn
        self.channel, self.connection = create_rabbitmq_client()

    def _publish(self, result: InferenceResult):
        self.channel.basic_publish(
            exchange="",
            routing_key=result.inference_id,
            properties=BasicProperties(headers={"inference_id": result.inference_id}),
            body=result.result,
        )

    def publish(self, result: InferenceResult):
        self.connection.add_callback_threadsafe(lambda: self._publish(result))

    def run(self):
        while self.is_running:
            self.connection.process_data_events(time_limit=self.wait_time)
            msgs = self.consumer.consume(self.max_size, self.wait_time)
            if not msgs:
                continue
            batch = [
                build_query(msg.key().decode("utf-8"), json.loads(msg.value())) for msg in msgs
            ]
            logger.debug("worker %s batch size %s", self.worker_id, len(batch))
            results = self.inference_fn(batch)
            for result in results:
                print(f"{self.worker_id} ---> {result}")
                self.publish(result)

    def stop(self):
        logger.info("stopping worker %s", self.worker_id)
        self.is_running = False
        # Wait until all the data events have been processed
        self.connection.process_data_events(time_limit=1)
        if self.connection.is_open:
            self.connection.close()
        self.consumer.close()
        logger.info("stopped worker %s", self.worker_id)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--n-workers", type=int, default=2, help="number of consumer workers.")
    parser.add_argument("--config-file", type=FileType("r"))
    args = parser.parse_args()

    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser["default"])
    config.update(config_parser["consumer"])
    print(config)

    tokenizer = T5Tokenizer.from_pretrained("t5-small", model_max_length=512)
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    model.load_state_dict(torch.load("/home/models/t5_small_ft_22.pth", map_location="cpu"))
    inference = create_inference(model, tokenizer)

    for i in range(args.n_workers):
        logger.info("launching consumer worker %s", i)
        consumer = InferenceConsumer(i, config, "inference_queue", inference)
        consumer.start()


if __name__ == "__main__":
    main()
