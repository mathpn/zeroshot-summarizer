#!/bin/bash

/wait
exec python -m consumer.worker --config-file /home/consumer/kafka_config.ini --n-workers $1