#!/bin/bash

/wait
# exec python -m consumer.worker
exec python -m consumer.worker --config-file /home/consumer/kafka_config.ini