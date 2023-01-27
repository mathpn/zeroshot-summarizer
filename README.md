# zeroshot-summarizer-v1

The goal of this project is to finetune a T5 transformer to take abstracts and return titles. Not only that, but the generated title should be costumizable according to some predefined adjectives.

There will be an API (FastAPI) to receive inference requests, which will be added to a RabbitMQ queue. An inference worker will consume this queue and store results in a Redis instance.
